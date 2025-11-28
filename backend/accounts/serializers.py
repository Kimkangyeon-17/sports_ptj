from rest_framework import serializers
from django.contrib.auth import get_user_model
from teams.models import Team

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
