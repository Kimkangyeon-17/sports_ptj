from matches.models import Match
from rest_framework import serializers
from django.contrib.auth import get_user_model
from teams.models import Team, TeamStanding
from django.utils import timezone
from django.db.models import Q


User = get_user_model()


class FavoriteTeamSerializer(serializers.ModelSerializer):
    """응원 팀 간단 정보"""

    class Meta:
        model = Team
        fields = ["team_id", "team_name", "league"]


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 시리얼라이저"""

    favorite_teams = FavoriteTeamSerializer(many=True, read_only=True)
    favorite_teams_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "nickname",
            "profile_image",
            "social_provider",
            "favorite_teams",
            "favorite_teams_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "social_provider"]


class UserRegisterSerializer(serializers.ModelSerializer):
    """회원가입 시리얼라이저"""

    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password2",
            "nickname",
        ]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class NextMatchSerializer(serializers.Serializer):
    """다음 경기 정보"""

    match_id = serializers.CharField()
    match_date = serializers.DateTimeField()
    opponent_name = serializers.CharField()
    opponent_logo = serializers.URLField()
    is_home = serializers.BooleanField()
    venue = serializers.CharField()


class RecentMatchSerializer(serializers.Serializer):
    """최근 경기 정보"""

    match_date = serializers.DateTimeField()
    opponent = serializers.CharField()
    result = serializers.CharField()  # W, D, L
    score = serializers.CharField()
    is_home = serializers.BooleanField()


class RecentFormSerializer(serializers.Serializer):
    """최근 폼"""

    form = serializers.CharField()  # WWDLW
    form_korean = serializers.CharField()  # 승-승-무-패-승
    last_5_matches = RecentMatchSerializer(many=True)


class TeamStandingSimpleSerializer(serializers.Serializer):
    """간단한 순위 정보"""

    rank = serializers.IntegerField()
    points = serializers.IntegerField()
    wins = serializers.IntegerField()
    draws = serializers.IntegerField()
    losses = serializers.IntegerField()
    win_rate = serializers.FloatField()
    matches_played = serializers.IntegerField()
    goals_for = serializers.IntegerField()
    goals_against = serializers.IntegerField()
    goal_difference = serializers.IntegerField()


class TeamDashboardSerializer(serializers.Serializer):
    """팀 대시보드 정보"""

    team_id = serializers.CharField()
    team_name = serializers.CharField()
    team_logo = serializers.URLField(required=False, allow_null=True)
    standing = TeamStandingSimpleSerializer(required=False, allow_null=True)
    next_match = NextMatchSerializer(required=False, allow_null=True)
    recent_form = RecentFormSerializer(required=False, allow_null=True)


class MainDashboardSerializer(serializers.Serializer):
    """메인 대시보드"""

    favorite_teams = TeamDashboardSerializer(many=True)
    latest_news = serializers.ListField(child=serializers.DictField(), default=[])
    ai_analysis = serializers.DictField(required=False, allow_null=True)
