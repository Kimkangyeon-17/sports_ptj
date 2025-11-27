from django.db import models


class Team(models.Model):
    team_id = models.CharField(max_length=50, unique=True)
    team_name = models.CharField(max_length=200)

    # 리그 정보
    league = models.CharField(max_length=100, blank=True)

    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["team_name"]
        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __str__(self):
        return self.team_name


class Staff(models.Model):
    """감독 및 코치 정보"""

    team_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)  # Manager, Assistant coach, etc.
    name = models.CharField(max_length=200)
    nationality = models.CharField(max_length=100, blank=True)

    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["team_name", "position", "name"]
        verbose_name = "Staff"
        verbose_name_plural = "Staff"
        indexes = [
            models.Index(fields=["team_name"]),
            models.Index(fields=["position"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.position} ({self.team_name})"


class TeamStanding(models.Model):
    """EPL 팀 순위 모델"""

    rank = models.IntegerField(verbose_name="순위")
    team_name = models.CharField(max_length=100, verbose_name="팀명")
    team_logo = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="팀 로고"
    )
    points = models.IntegerField(verbose_name="승점")
    matches_played = models.IntegerField(verbose_name="경기수")
    wins = models.IntegerField(verbose_name="승")
    draws = models.IntegerField(verbose_name="무")
    losses = models.IntegerField(verbose_name="패")
    goals_for = models.IntegerField(verbose_name="득점")
    goals_against = models.IntegerField(verbose_name="실점")
    goal_difference = models.IntegerField(verbose_name="득실차")

    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["rank"]
        verbose_name = "팀 순위"
        verbose_name_plural = "팀 순위들"

    def __str__(self):
        return f"{self.rank}. {self.team_name}"
