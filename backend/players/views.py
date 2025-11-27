from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Player
from .serializers import PlayerSerializer, PlayerDetailSerializer


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    선수 정보 조회 API
    - list: 선수 목록 조회
    - retrieve: 선수 상세 조회
    - search: 선수 검색
    """

    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "full_name", "team_name", "nationality"]
    ordering_fields = ["name", "age", "team_name"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PlayerDetailSerializer
        return PlayerSerializer

    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        선수 검색
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
