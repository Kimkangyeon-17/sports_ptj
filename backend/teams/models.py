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
