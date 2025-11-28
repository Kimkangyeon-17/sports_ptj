from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """커스텀 유저 모델"""

    email = models.EmailField(unique=True, verbose_name="이메일")
    nickname = models.CharField(max_length=50, blank=True, verbose_name="닉네임")
    profile_image = models.URLField(blank=True, null=True, verbose_name="프로필 이미지")

    # 소셜 로그인 정보
    social_provider = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ("kakao", "Kakao"),
            ("naver", "Naver"),
            ("google", "Google"),
        ],
        verbose_name="소셜 로그인 제공자",
    )
    social_id = models.CharField(max_length=200, blank=True, verbose_name="소셜 ID")

    # 응원 팀 (최대 3개)
    favorite_teams = models.ManyToManyField(
        "teams.Team", blank=True, related_name="fans", verbose_name="응원 팀"
    )

    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "사용자"
        verbose_name_plural = "사용자들"

    def __str__(self):
        return self.username

    def add_favorite_team(self, team):
        """응원 팀 추가 (최대 3개 제한)"""
        if self.favorite_teams.count() >= 3:
            raise ValidationError("응원 팀은 최대 3개까지만 선택할 수 있습니다.")
        self.favorite_teams.add(team)

    def remove_favorite_team(self, team):
        """응원 팀 제거"""
        self.favorite_teams.remove(team)

    @property
    def favorite_teams_count(self):
        """응원 팀 개수"""
        return self.favorite_teams.count()
