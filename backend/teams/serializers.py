from rest_framework import serializers
from .models import Team, Staff, TeamStanding


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = [
            # "id",
            "team_id",
            "team_name",
            "league",
        ]


class TeamDetailSerializer(serializers.ModelSerializer):
    """팀 상세 정보용 시리얼라이저"""

    class Meta:
        model = Team
        fields = "__all__"


class StaffSerializer(serializers.ModelSerializer):
    """감독/코치 시리얼라이저"""

    class Meta:
        model = Staff
        fields = [
            # "id",
            "team_name",
            "position",
            "name",
            # "nationality",
        ]


class StaffDetailSerializer(serializers.ModelSerializer):
    """감독/코치 상세 정보용 시리얼라이저"""

    class Meta:
        model = Staff
        fields = "__all__"


class TeamStandingSerializer(serializers.ModelSerializer):
    """팀 순위표 시리얼라이저"""

    class Meta:
        model = TeamStanding
        fields = [
            "id",
            "rank",
            "team_name",
            "team_logo",
            "points",
            "matches_played",
            "wins",
            "draws",
            "losses",
            "goals_for",
            "goals_against",
            "goal_difference",
            "updated_at",
        ]
