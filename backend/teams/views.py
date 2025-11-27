import os
from datetime import date
from django.conf import settings
from django.core.management import call_command
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Team, Staff, TeamStanding
from .serializers import (
    TeamSerializer,
    TeamDetailSerializer,
    StaffSerializer,
    StaffDetailSerializer,
    TeamStandingSerializer,
)
from players.models import Player
from players.serializers import PlayerSerializer


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    팀 정보 조회 API
    - list: 팀 목록 조회
    - retrieve: 팀 상세 조회
    - players: 팀 소속 선수 목록
    """

    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["team_name", "league"]
    ordering_fields = ["team_name"]
    ordering = ["team_name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TeamDetailSerializer
        return TeamSerializer

    @action(detail=True, methods=["get"])
    def players(self, request, pk=None):
        """
        팀 소속 선수 목록 조회
        """
        team = self.get_object()
        players = Player.objects.filter(team_id=team.team_id)

        # 포지션별 필터
        position = request.query_params.get("position", None)
        if position:
            players = players.filter(position__icontains=position)

        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        팀 검색
        query params: name, league
        """
        queryset = self.get_queryset()

        # 팀 이름 검색
        name = request.query_params.get("name", None)
        if name:
            queryset = queryset.filter(team_name__icontains=name)

        # 리그 검색
        league = request.query_params.get("league", None)
        if league:
            queryset = queryset.filter(league__icontains=league)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class StaffViewSet(viewsets.ReadOnlyModelViewSet):
    """
    감독/코치 정보 조회 API
    - list: 감독/코치 목록 조회
    - retrieve: 감독/코치 상세 조회
    - search: 감독/코치 검색
    """

    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "team_name", "position", "nationality"]
    ordering_fields = ["name", "team_name", "position"]
    ordering = ["team_name", "position"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StaffDetailSerializer
        return StaffSerializer

    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        감독/코치 검색
        query params: name, team, position, nationality
        """
        queryset = self.get_queryset()

        # 이름 검색
        name = request.query_params.get("name", None)
        if name:
            queryset = queryset.filter(name__icontains=name)

        # 팀 검색
        team = request.query_params.get("team", None)
        if team:
            queryset = queryset.filter(team_name__icontains=team)

        # 포지션 검색
        position = request.query_params.get("position", None)
        if position:
            queryset = queryset.filter(position__icontains=position)

        # 국적 검색
        nationality = request.query_params.get("nationality", None)
        if nationality:
            queryset = queryset.filter(nationality__icontains=nationality)

        # 페이지네이션 적용
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TeamStandingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    팀 순위표 조회 API
    - list: 순위표 전체 조회
    - retrieve: 특정 팀 순위 조회
    - 자동 업데이트: 오늘 날짜 데이터가 없으면 자동으로 update_standings 실행
    """

    queryset = TeamStanding.objects.all()
    serializer_class = TeamStandingSerializer

    def list(self, request, *args, **kwargs):
        """
        순위표 목록 조회 전에 자동으로 업데이트 체크
        """
        self.check_and_update_standings()
        return super().list(request, *args, **kwargs)

    def check_and_update_standings(self):
        """
        오늘 날짜의 CSV 파일이 없으면 자동으로 업데이트 실행
        """
        csv_dir = os.path.join(settings.BASE_DIR, "data", "standings")
        today = date.today()
        csv_filename = os.path.join(
            csv_dir, f'epl_standings_{today.strftime("%Y_%m_%d")}.csv'
        )

        # 오늘 날짜 CSV 파일이 없으면 업데이트 실행
        if not os.path.exists(csv_filename):
            try:
                print(
                    f"📡 오늘({today}) 순위표 데이터가 없습니다. 자동 업데이트를 시작합니다..."
                )
                call_command("update_standings")
                print("✓ 자동 업데이트 완료!")
            except Exception as e:
                print(f"⚠️  자동 업데이트 실패: {e}")

    @action(detail=False, methods=["get"])
    def top(self, request):
        """
        상위 N팀 조회
        query params: n (기본값: 5)
        """
        self.check_and_update_standings()
        n = int(request.query_params.get("n", 5))
        top_teams = TeamStanding.objects.all()[:n]
        serializer = self.get_serializer(top_teams, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def bottom(self, request):
        """
        하위 N팀 조회 (강등권)
        query params: n (기본값: 3)
        """
        self.check_and_update_standings()
        n = int(request.query_params.get("n", 3))
        bottom_teams = TeamStanding.objects.all().order_by("-rank")[:n]
        serializer = self.get_serializer(bottom_teams, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def force_update(self, request):
        """
        수동으로 순위표 강제 업데이트
        POST /api/standings/force_update/
        """
        try:
            call_command("update_standings", "--force")
            return Response(
                {
                    "status": "success",
                    "message": "순위표가 성공적으로 업데이트되었습니다.",
                }
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": f"업데이트 실패: {str(e)}"}, status=500
            )
