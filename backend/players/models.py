from django.db import models


class Player(models.Model):
    # 기본 정보
    player_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    # 위키 정보
    wiki_name = models.CharField(max_length=200, blank=True)
    wiki_url = models.URLField(blank=True)
    wiki_found = models.BooleanField(default=False)

    # 포지션 정보
    position = models.CharField(max_length=50)
    position_abbr = models.CharField(max_length=10)
    jersey_number = models.CharField(max_length=10, blank=True)

    # 신체 정보
    age = models.IntegerField(null=True, blank=True)
    height = models.CharField(max_length=20, blank=True)
    weight = models.CharField(max_length=20, blank=True)

    # 출생 정보
    birth_place = models.CharField(max_length=200, blank=True)
    birth_date = models.DateTimeField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)

    # 팀 정보
    team_id = models.CharField(max_length=50, blank=True)
    team_name = models.CharField(max_length=200, blank=True)

    # 추가 정보 (JSON 데이터용)
    introduction = models.TextField(blank=True)
    playing_style = models.TextField(blank=True)
    career_summary = models.TextField(blank=True)

    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Player"
        verbose_name_plural = "Players"

    def __str__(self):
        return f"{self.name} ({self.team_name})"
