from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 시리얼라이저"""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "nickname",
            "profile_image",
            "social_provider",
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
