from rest_framework import serializers
from .models import Match


class MatchSerializer(serializers.ModelSerializer):
    """경기 정보 시리얼라이저"""

    is_finished = serializers.BooleanField(read_only=True)
    is_live = serializers.BooleanField(read_only=True)

    class Meta:
        model = Match
        fields = [
            "match_id",
            "competition",
            "season",
            "matchday",
            "match_date",
            "home_team_id",
            "home_team_name",
            "home_team_logo",
            "away_team_id",
            "away_team_name",
            "away_team_logo",
            "home_score",
            "away_score",
            "status",
            "venue",
            "home_half_score",
            "away_half_score",
            "is_finished",
            "is_live",
            "updated_at",
        ]


class MatchListSerializer(serializers.ModelSerializer):
    """경기 목록용 간단한 시리얼라이저"""

    is_finished = serializers.BooleanField(read_only=True)
    is_live = serializers.BooleanField(read_only=True)

    class Meta:
        model = Match
        fields = [
            "match_id",
            "matchday",
            "match_date",
            "home_team_name",
            "home_team_logo",
            "away_team_name",
            "away_team_logo",
            "home_score",
            "away_score",
            "status",
            "is_finished",
            "is_live",
        ]
