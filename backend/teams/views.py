from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Team, Staff
from .serializers import (
    TeamSerializer,
    TeamDetailSerializer,
    StaffSerializer,
    StaffDetailSerializer,
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
