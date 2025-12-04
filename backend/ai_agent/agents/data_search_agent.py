"""
Data Search Agent
- Django ORM을 사용한 실제 DB 검색
"""

from django.db.models import Q
from teams.models import Team, TeamStanding
from players.models import Player
from matches.models import Match
from ai_agent.utils import normalize_team_name, normalize_player_name


class SportsDataSearchAgent:
    """스포츠 데이터 검색 Agent"""

    def search_with_metadata(self, state: dict) -> dict:
        """의도에 따라 적절한 데이터 검색"""
        intent = state.get("intent", "")
        team_name = state.get("team_name")
        player_name = state.get("player_name")
        date_range = state.get("date_range")

        # 팀명/선수명 정규화 (한글 → 영문)
        if team_name:
            team_name = normalize_team_name(team_name)
        if player_name:
            player_name = normalize_player_name(player_name)

        print(f"\n🔎 데이터 검색 중...")
        print(f"   의도: {intent}")
        print(f"   팀명: {team_name}")
        print(f"   선수명: {player_name}")

        search_results = {}

        try:
            # 의도별 검색
            if intent == "경기_일정":
                search_results["matches"] = self._search_matches(team_name, date_range)
                print(f"   ✅ {len(search_results['matches'])}개 경기 검색됨")

            elif intent == "팀_정보":
                search_results["team"] = self._search_team(team_name)
                search_results["recent_matches"] = self._search_matches(
                    team_name, "recent", limit=5
                )
                print(f"   ✅ 팀 정보 및 최근 경기 검색됨")

            elif intent == "선수_정보":
                search_results["player"] = self._search_player(player_name)
                print(f"   ✅ 선수 정보 검색 완료")

            elif intent == "순위_정보":
                if team_name:
                    search_results["standing"] = self._search_standing(team_name)
                    print(f"   ✅ {team_name} 순위 검색됨")
                else:
                    search_results["standings"] = self._search_all_standings()
                    print(f"   ✅ {len(search_results['standings'])}개 팀 순위 검색됨")

            elif intent == "분석_요청":
                search_results["matches"] = self._search_matches(
                    team_name, "recent", limit=10
                )
                print(f"   ✅ 분석용 경기 데이터 검색됨")

        except Exception as e:
            print(f"   ❌ 검색 오류: {e}")
            import traceback

            traceback.print_exc()

        return {
            **state,
            "search_results": search_results,
        }

    def _search_matches(
        self,
        team_name: str | None = None,
        date_range: str | None = None,
        limit: int = 10,
    ) -> list:
        """경기 검색"""
        from datetime import datetime

        try:
            query = Match.objects.all()

            if team_name:
                query = query.filter(
                    Q(home_team_name__iexact=team_name)
                    | Q(away_team_name__iexact=team_name)
                )

            now = datetime.now()
            if date_range == "recent":
                query = query.filter(match_date__lt=now).order_by("-match_date")
            elif date_range == "upcoming":
                query = query.filter(match_date__gte=now).order_by("match_date")
            else:
                query = query.order_by("match_date")

            matches = query[:limit]

            return [
                {
                    "id": m.id,
                    "match_date": m.match_date.isoformat() if m.match_date else None,
                    "home_team": m.home_team_name or "미정",
                    "away_team": m.away_team_name or "미정",
                    "home_score": m.home_score,
                    "away_score": m.away_score,
                    "status": m.status,
                    "venue": m.venue or "미정",
                }
                for m in matches
            ]

        except Exception as e:
            print(f"경기 검색 오류: {e}")
            import traceback

            traceback.print_exc()
            return []

    def _search_team(self, team_name: str | None) -> dict | None:
        """팀 정보 검색"""
        if not team_name:
            return None

        try:
            team = Team.objects.filter(team_name__iexact=team_name).first()

            if not team:
                return None

            return {
                "team_id": team.team_id,
                "team_name": team.team_name,
                "league": team.league,
                # "fans": team.fans,  # ManyToMany 제외
            }

        except Exception as e:
            print(f"팀 검색 오류: {e}")
            import traceback

            traceback.print_exc()
            return None

    def _search_standing(self, team_name: str) -> dict | None:
        """팀 순위 검색"""
        try:
            standing = TeamStanding.objects.filter(team_name__iexact=team_name).first()

            if not standing:
                return None

            return {
                "rank": standing.rank,
                "team_name": standing.team_name,
            }

        except Exception as e:
            print(f"순위 검색 오류: {e}")
            return None

    def _search_all_standings(self) -> list:
        """전체 순위표 검색"""
        try:
            standings = TeamStanding.objects.order_by("rank")[:20]

            return [
                {
                    "rank": s.rank,
                    "team_name": s.team_name,
                }
                for s in standings
            ]

        except Exception as e:
            print(f"전체 순위표 검색 오류: {e}")
            return []

    def _search_player(self, player_name: str | None) -> dict | None:
        """
        선수 정보 검색

        Args:
            player_name: 선수명 (영문)

        Returns:
            선수 정보 또는 None
        """
        if not player_name:
            return None

        try:
            # 1. 정확한 이름 검색
            player = Player.objects.filter(name__iexact=player_name).first()

            if not player:
                # 2. 부분 검색 (Salah → Mohamed Salah)
                player = Player.objects.filter(name__icontains=player_name).first()

            if not player:
                print(f"   ⚠️  선수 '{player_name}' 검색 실패")
                return None

            print(f"   ✅ 선수 찾음: {player.name}")

            return {
                "name": player.name,
                "team": player.team_name or "소속팀 없음",
                "position": player.position or "포지션 정보 없음",
                "nationality": player.nationality or "국적 정보 없음",
                "age": player.age if player.age else None,
                "jersey_number": (
                    player.jersey_number if hasattr(player, "jersey_number") else None
                ),
            }

        except Exception as e:
            print(f"선수 검색 오류: {e}")
            import traceback

            traceback.print_exc()
            return None
