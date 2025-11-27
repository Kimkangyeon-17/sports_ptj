from rest_framework import serializers
from .models import Team, Staff


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = [
            "id",
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
            "id",
            "team_name",
            "position",
            "name",
            "nationality",
        ]


class StaffDetailSerializer(serializers.ModelSerializer):
    """감독/코치 상세 정보용 시리얼라이저"""

    class Meta:
        model = Staff
        fields = "__all__"
