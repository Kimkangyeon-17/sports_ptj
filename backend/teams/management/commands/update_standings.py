"""
EPL 순위표 자동 업데이트 - Django Management Command
- ESPN API로 최신 데이터 수집
- 팀 로고 이미지 포함
- CSV 파일 자동 생성 (날짜별)
- DB 자동 반영
- 하루에 한 번만 실행 (중복 방지)
"""

import os
import requests
import pandas as pd
from datetime import datetime, date
from typing import Optional, Dict
from django.core.management.base import BaseCommand
from django.conf import settings
from teams.models import TeamStanding


class Command(BaseCommand):
    help = "ESPN API로 최신 EPL 순위표를 가져와서 CSV 저장 후 DB를 업데이트합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="강제로 업데이트 (날짜 체크 무시)",
        )

    def handle(self, *args, **options):
        force_update = options.get("force", False)

        self.stdout.write("=" * 70)
        self.stdout.write(
            self.style.SUCCESS("  EPL 순위표 자동 업데이트 (팀 로고 포함)")
        )
        self.stdout.write("=" * 70)

        # CSV 저장 경로 설정
        csv_dir = os.path.join(settings.BASE_DIR, "data", "standings")
        os.makedirs(csv_dir, exist_ok=True)

        today = date.today()
        csv_filename = os.path.join(
            csv_dir, f'epl_standings_{today.strftime("%Y_%m_%d")}.csv'
        )

        # 오늘 날짜의 CSV 파일이 이미 있는지 확인
        if os.path.exists(csv_filename) and not force_update:
            self.stdout.write(
                self.style.WARNING(f"\n✓ 오늘({today}) 데이터가 이미 존재합니다.")
            )
            self.stdout.write(f"  파일: {csv_filename}")
            self.stdout.write(
                "\n  강제 업데이트: python manage.py update_standings --force"
            )
            return

        # 1. 팀 로고 정보 먼저 가져오기
        self.stdout.write(f"\n🎨 팀 로고 정보 수집 중...")
        team_logos = self.get_team_logos()

        if team_logos:
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ {len(team_logos)}개 팀 로고 수집 완료")
            )
        else:
            self.stdout.write(
                self.style.WARNING("  ⚠️  팀 로고 수집 실패 (순위표는 계속 진행)")
            )

        # 2. ESPN API에서 최신 순위표 가져오기
        self.stdout.write(f"\n📡 ESPN API에서 최신 순위표 가져오는 중...")

        df = self.get_epl_standings_from_espn(team_logos)

        if df is None or df.empty:
            self.stdout.write(self.style.ERROR("\n✗ 데이터 수집 실패!"))
            return

        # 3. CSV 파일로 저장
        self.stdout.write(f"\n💾 CSV 파일 저장 중...")
        df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
        self.stdout.write(self.style.SUCCESS(f"  ✓ 저장 완료: {csv_filename}"))

        # 4. DB 업데이트
        self.stdout.write(f"\n🗄️  데이터베이스 업데이트 중...")
        updated_count = self.update_database(df)

        if updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ {updated_count}개 팀 데이터 업데이트 완료!")
            )

            # 업데이트 결과 출력
            self.print_standings_summary(df)
        else:
            self.stdout.write(self.style.ERROR("  ✗ 데이터베이스 업데이트 실패!"))

        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("✅ 업데이트 완료!"))
        self.stdout.write("=" * 70)

    def get_team_logos(self) -> Dict[str, str]:
        """
        ESPN API로 모든 팀의 로고 URL 가져오기
        Returns: {팀명: 로고URL} 딕셔너리
        """
        url = "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/teams"

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()

            teams = data["sports"][0]["leagues"][0]["teams"]

            team_logos = {}
            for team_data in teams:
                team = team_data["team"]
                team_name = team.get("displayName", "")

                # 로고 URL 추출
                logo_url = ""
                if team.get("logos") and len(team["logos"]) > 0:
                    logo_url = team["logos"][0].get("href", "")

                if team_name and logo_url:
                    team_logos[team_name] = logo_url

            return team_logos

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  ⚠️  팀 로고 조회 실패: {e}"))
            return {}

    def get_epl_standings_from_espn(
        self, team_logos: Dict[str, str]
    ) -> Optional[pd.DataFrame]:
        """
        ESPN API로 EPL 순위표 가져오기 (팀 로고 포함)
        """
        current_year = datetime.now().year
        season = current_year

        url = "https://site.api.espn.com/apis/v2/sports/soccer/eng.1/standings"
        params = {"season": season}

        try:
            self.stdout.write(f"  → API 호출: {url}")
            self.stdout.write(f"  → 시즌: {season-1}-{season}")

            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            # 순위표 데이터 추출
            if "children" in data and data["children"]:
                standings = data["children"][0]["standings"]["entries"]
            elif "standings" in data:
                standings = data["standings"]["entries"]
            else:
                self.stdout.write(self.style.ERROR("  ✗ 순위표 데이터를 찾을 수 없음"))
                return None

            self.stdout.write(f"  ✓ {len(standings)}개 팀 데이터 수신")

            # 데이터 파싱
            teams = []
            for team in standings:
                try:
                    # 통계 데이터를 딕셔너리로 변환
                    stats = {}
                    if "stats" in team:
                        for stat in team["stats"]:
                            stat_name = stat.get("name", "")
                            stat_value = stat.get("value", stat.get("displayValue", 0))
                            stats[stat_name] = stat_value

                    team_name = team["team"]["displayName"]

                    # 팀 로고 URL 가져오기
                    team_logo = team_logos.get(team_name, "")

                    team_info = {
                        "순위": int(stats.get("rank", team.get("id", 0))),
                        "팀명": team_name,
                        "팀로고": team_logo,
                        "승점": int(float(stats.get("points", 0))),
                        "경기수": int(float(stats.get("gamesPlayed", 0))),
                        "승": int(float(stats.get("wins", 0))),
                        "무": int(float(stats.get("ties", 0))),
                        "패": int(float(stats.get("losses", 0))),
                        "득점": int(float(stats.get("pointsFor", 0))),
                        "실점": int(float(stats.get("pointsAgainst", 0))),
                        "득실차": int(float(stats.get("pointDifferential", 0))),
                    }
                    teams.append(team_info)
                except Exception as e:
                    team_name = team.get("team", {}).get("displayName", "Unknown")
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠️  '{team_name}' 파싱 실패: {e}")
                    )
                    continue

            # DataFrame 생성 및 정렬
            df = pd.DataFrame(teams)
            df = df.sort_values("순위").reset_index(drop=True)

            # 로고가 있는 팀 개수 확인
            logo_count = df["팀로고"].astype(bool).sum()
            self.stdout.write(
                f"  ✓ DataFrame 생성 완료: {len(df)}개 팀 (로고 {logo_count}개)"
            )

            return df

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"  ✗ API 호출 실패: {e}"))
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ 예상치 못한 오류: {e}"))
            import traceback

            traceback.print_exc()
            return None

    def update_database(self, df: pd.DataFrame) -> int:
        """DataFrame의 데이터를 DB에 저장 (팀 로고 포함)"""
        try:
            # 기존 데이터 모두 삭제
            deleted_count = TeamStanding.objects.all().count()
            TeamStanding.objects.all().delete()
            self.stdout.write(f"  → 기존 {deleted_count}개 데이터 삭제")

            # 새 데이터 삽입
            created_count = 0
            for _, row in df.iterrows():
                TeamStanding.objects.create(
                    rank=row["순위"],
                    team_name=row["팀명"],
                    team_logo=row["팀로고"] if row["팀로고"] else None,
                    points=row["승점"],
                    matches_played=row["경기수"],
                    wins=row["승"],
                    draws=row["무"],
                    losses=row["패"],
                    goals_for=row["득점"],
                    goals_against=row["실점"],
                    goal_difference=row["득실차"],
                )
                created_count += 1

            self.stdout.write(f"  → {created_count}개 새 데이터 생성")

            return created_count

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ DB 업데이트 오류: {e}"))
            import traceback

            traceback.print_exc()
            return 0

    def print_standings_summary(self, df: pd.DataFrame):
        """순위표 요약 출력"""
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("📊 현재 EPL 순위표")
        self.stdout.write("=" * 70)

        # 상위 5팀
        self.stdout.write("\n🏆 상위 5팀:")
        for i in range(min(5, len(df))):
            row = df.iloc[i]
            logo_status = "🎨" if row["팀로고"] else "  "
            self.stdout.write(
                f"  {logo_status} {row['순위']:2d}위. {row['팀명']:25s} "
                f"{row['승점']:2d}점 ({row['승']}승 {row['무']}무 {row['패']}패)"
            )

        # 강등권 팀
        if len(df) >= 18:
            self.stdout.write("\n⚠️  강등권 (18-20위):")
            for i in range(max(0, len(df) - 3), len(df)):
                row = df.iloc[i]
                logo_status = "🎨" if row["팀로고"] else "  "
                self.stdout.write(
                    f"  {logo_status} {row['순위']:2d}위. {row['팀명']:25s} "
                    f"{row['승점']:2d}점 ({row['승']}승 {row['무']}무 {row['패']}패)"
                )

        # 통계
        self.stdout.write("\n📈 시즌 통계:")
        self.stdout.write(f"  🥇 1위: {df.iloc[0]['팀명']} ({df.iloc[0]['승점']}점)")
        self.stdout.write(
            f"  ⚽ 최다득점: {df.loc[df['득점'].idxmax()]['팀명']} ({df['득점'].max()}골)"
        )
        self.stdout.write(
            f"  🛡️  최소실점: {df.loc[df['실점'].idxmin()]['팀명']} ({df['실점'].min()}골)"
        )

        # 로고 통계
        logo_count = df["팀로고"].astype(bool).sum()
        self.stdout.write(f"  🎨 팀 로고: {logo_count}/{len(df)}개")
