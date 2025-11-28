from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from datetime import timedelta
from .models import Match
from .serializers import MatchSerializer, MatchListSerializer
from django.core.management import call_command


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """경기 일정 및 결과 ViewSet"""

    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        """액션에 따라 다른 시리얼라이저 사용"""
        if self.action == "list":
            return MatchListSerializer
        return MatchSerializer

    def list(self, request, *args, **kwargs):
        """경기 목록 조회 (자동 업데이트 포함)"""
        # 데이터 자동 업데이트
        self.check_and_update_matches()
        return super().list(request, *args, **kwargs)

    def check_and_update_matches(self):
        """경기 데이터 자동 업데이트 (하루에 한 번)"""
        try:
            # 가장 최근 업데이트된 경기 확인
            latest_match = Match.objects.order_by("-updated_at").first()

            if latest_match:
                time_diff = timezone.now() - latest_match.updated_at
                # 1시간 이상 지났으면 업데이트
                if time_diff > timedelta(hours=1):
                    call_command("update_matches")
            else:
                # 경기 데이터가 없으면 업데이트
                call_command("update_matches")
        except Exception as e:
            print(f"자동 업데이트 실패: {e}")

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """예정된 경기 목록"""
        now = timezone.now()
        matches = self.queryset.filter(
            match_date__gte=now, status="scheduled"
        ).order_by("match_date")[:10]

        serializer = self.get_serializer(matches, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def live(self, request):
        """진행 중인 경기 목록"""
        matches = self.queryset.filter(status="live")
        serializer = self.get_serializer(matches, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def finished(self, request):
        """종료된 경기 목록"""
        matches = self.queryset.filter(status="finished").order_by("-match_date")[:20]
        serializer = self.get_serializer(matches, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_date(self, request):
        """날짜별 경기 조회 (?date=2024-11-27)"""
        date_str = request.query_params.get("date")

        if not date_str:
            return Response(
                {"error": "date 파라미터가 필요합니다. (형식: YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from datetime import datetime

            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            matches = self.queryset.filter(match_date__date=target_date).order_by(
                "match_date"
            )

            serializer = self.get_serializer(matches, many=True)
            return Response(serializer.data)

        except ValueError:
            return Response(
                {"error": "올바른 날짜 형식이 아닙니다. (YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"])
    def by_team(self, request):
        """팀별 경기 조회 (?team_id=123 또는 ?team_name=Arsenal)"""
        team_id = request.query_params.get("team_id")
        team_name = request.query_params.get("team_name")

        if not team_id and not team_name:
            return Response(
                {"error": "team_id 또는 team_name 파라미터가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.db.models import Q

        if team_id:
            matches = self.queryset.filter(
                Q(home_team_id=team_id) | Q(away_team_id=team_id)
            ).order_by("-match_date")
        else:
            matches = self.queryset.filter(
                Q(home_team_name__icontains=team_name)
                | Q(away_team_name__icontains=team_name)
            ).order_by("-match_date")

        serializer = self.get_serializer(matches, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_matchday(self, request):
        """라운드별 경기 조회 (?matchday=15)"""
        matchday = request.query_params.get("matchday")

        if not matchday:
            return Response(
                {"error": "matchday 파라미터가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            matchday = int(matchday)
            matches = self.queryset.filter(matchday=matchday).order_by("match_date")
            serializer = self.get_serializer(matches, many=True)
            return Response(serializer.data)

        except ValueError:
            return Response(
                {"error": "matchday는 숫자여야 합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["post"])
    def force_update(self, request):
        """강제로 경기 데이터 업데이트"""
        try:
            call_command("update_matches", "--force")
            return Response({"message": "경기 데이터가 업데이트되었습니다."})
        except Exception as e:
            return Response(
                {"error": f"업데이트 실패: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
