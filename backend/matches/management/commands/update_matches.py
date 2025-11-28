from django.core.management.base import BaseCommand
from matches.models import Match
import requests
from datetime import datetime
import pytz


class Command(BaseCommand):
    help = "ESPN API에서 EPL 경기 일정 및 결과 업데이트"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="강제로 모든 데이터 업데이트",
        )

    def handle(self, *args, **options):
        self.stdout.write("경기 일정 업데이트 시작...")

        from datetime import date, timedelta

        # EPL 2025-26 시즌 (2025년 8월 ~ 2026년 5월)
        start_date = date(2025, 8, 1)  # 2025-26 시즌 시작
        end_date = date(2026, 5, 31)  # 2025-26 시즌 종료

        self.stdout.write(
            f"📅 2025-26 시즌: {start_date} ~ {end_date} 경기 데이터 수집 시작"
        )

        total_created = 0
        total_updated = 0

        # 10일씩 나눠서 호출 (ESPN API 제한 고려)
        current_date = start_date

        while current_date <= end_date:
            batch_end = min(current_date + timedelta(days=9), end_date)

            date_param = (
                f"{current_date.strftime('%Y%m%d')}-{batch_end.strftime('%Y%m%d')}"
            )
            api_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates={date_param}"

            self.stdout.write(f"\n📅 {current_date} ~ {batch_end} 경기 조회 중...")

            try:
                # API 호출
                response = requests.get(api_url, timeout=10)
                response.raise_for_status()
                data = response.json()

                # 경기 데이터 파싱
                events = data.get("events", [])

                if not events:
                    self.stdout.write(f"  ℹ️  해당 기간에 경기가 없습니다.")
                else:
                    self.stdout.write(f"  📊 {len(events)}개 경기 발견")

                    for event in events:
                        match_data = self.parse_match_data(event)

                        if match_data:
                            match, created = Match.objects.update_or_create(
                                match_id=match_data["match_id"], defaults=match_data
                            )

                            if created:
                                total_created += 1
                                self.stdout.write(f"  ✅ 새 경기 추가: {match}")
                            else:
                                total_updated += 1
                                self.stdout.write(f"  🔄 경기 업데이트: {match}")

            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"  ❌ API 호출 실패: {e}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ 오류 발생: {e}"))

            # 다음 배치로
            current_date = batch_end + timedelta(days=1)

        self.stdout.write(
            self.style.SUCCESS(
                f"\n\n🎉 완료! 새로 추가: {total_created}개, 업데이트: {total_updated}개"
            )
        )

    def parse_match_data(self, event):
        """ESPN API 이벤트 데이터를 Match 모델 형식으로 변환"""
        try:
            match_id = event.get("id")

            # 날짜 파싱
            date_str = event.get("date")
            match_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

            # 대회 정보
            season_data = event.get("season", {})
            season = season_data.get("year", "")

            # competitions 배열에서 첫 번째 항목 가져오기
            competitions = event.get("competitions", [])
            if not competitions:
                self.stdout.write(
                    self.style.WARNING(f"경기 {match_id}: competitions 데이터 없음")
                )
                return None

            competition = competitions[0]

            # 라운드 정보 (week는 competitions 안에 있을 수 있음)
            matchday = competition.get("week")

            # 경기 상태
            status_data = competition.get("status", {})
            status_type = status_data.get("type", {}).get("name", "STATUS_SCHEDULED")
            state = status_data.get("type", {}).get("state", "")
            completed = status_data.get("type", {}).get("completed", False)

            # 팀 정보
            competitors = competition.get("competitors", [])

            if len(competitors) < 2:
                self.stdout.write(self.style.WARNING(f"경기 {match_id}: 팀 정보 부족"))
                return None

            # 홈팀/원정팀 구분
            home_team = None
            away_team = None

            for competitor in competitors:
                if competitor.get("homeAway") == "home":
                    home_team = competitor
                elif competitor.get("homeAway") == "away":
                    away_team = competitor

            if not home_team or not away_team:
                self.stdout.write(
                    self.style.WARNING(f"경기 {match_id}: 홈/원정 구분 실패")
                )
                return None

            # 디버그: 경기 정보 및 상태 출력
            self.stdout.write(
                f"  경기: {home_team.get('team', {}).get('displayName', '')} vs {away_team.get('team', {}).get('displayName', '')}"
            )
            self.stdout.write(
                f"    status_type: {status_type}, state: {state}, completed: {completed}"
            )

            status_map = {
                "STATUS_SCHEDULED": "scheduled",
                "STATUS_IN_PROGRESS": "live",
                "STATUS_FINAL": "finished",
                "STATUS_FULL_TIME": "finished",  # 추가
                "STATUS_HALFTIME": "live",
                "STATUS_POSTPONED": "postponed",
                "STATUS_CANCELED": "cancelled",
                "STATUS_CANCELLED": "cancelled",
            }
            status = status_map.get(status_type, "scheduled")

            # 경기장 정보
            venue_data = competition.get("venue", {})
            venue = venue_data.get("fullName", "")

            # 점수 파싱 (문자열을 정수로 변환)
            home_score = home_team.get("score")
            away_score = away_team.get("score")

            # 점수가 문자열인 경우 정수로 변환, 없으면 None
            try:
                home_score = int(home_score) if home_score else None
            except (ValueError, TypeError):
                home_score = None

            try:
                away_score = int(away_score) if away_score else None
            except (ValueError, TypeError):
                away_score = None

            match_data = {
                "match_id": match_id,
                "competition": "Premier League",
                "season": str(season),
                "matchday": matchday,
                "match_date": match_date,
                "home_team_id": home_team.get("id", ""),
                "home_team_name": home_team.get("team", {}).get("displayName", ""),
                "home_team_logo": home_team.get("team", {}).get("logo", ""),
                "away_team_id": away_team.get("id", ""),
                "away_team_name": away_team.get("team", {}).get("displayName", ""),
                "away_team_logo": away_team.get("team", {}).get("logo", ""),
                "home_score": home_score,
                "away_score": away_score,
                "status": status,
                "venue": venue,
            }

            # 전반전 점수 (있는 경우)
            linescores = home_team.get("linescores", [])
            if linescores and len(linescores) > 0:
                try:
                    match_data["home_half_score"] = int(linescores[0].get("value", 0))
                except (ValueError, TypeError):
                    match_data["home_half_score"] = None

            linescores = away_team.get("linescores", [])
            if linescores and len(linescores) > 0:
                try:
                    match_data["away_half_score"] = int(linescores[0].get("value", 0))
                except (ValueError, TypeError):
                    match_data["away_half_score"] = None

            return match_data

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"데이터 파싱 오류 (match_id: {match_id}): {e}")
            )
            import traceback

            self.stdout.write(traceback.format_exc())
            return None
