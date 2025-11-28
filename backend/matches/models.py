from django.db import models


class Match(models.Model):
    """경기 정보 모델"""
    
    STATUS_CHOICES = [
        ('scheduled', '예정'),
        ('live', '진행중'),
        ('finished', '종료'),
        ('postponed', '연기'),
        ('cancelled', '취소'),
    ]
    
    # ESPN API 고유 ID
    match_id = models.CharField(max_length=100, unique=True, verbose_name='경기 ID')
    
    # 경기 기본 정보
    competition = models.CharField(max_length=200, default='Premier League', verbose_name='대회명')
    season = models.CharField(max_length=50, verbose_name='시즌')
    matchday = models.IntegerField(null=True, blank=True, verbose_name='라운드')
    
    # 날짜 및 시간
    match_date = models.DateTimeField(verbose_name='경기 날짜')
    
    # 팀 정보
    home_team_id = models.CharField(max_length=100, verbose_name='홈팀 ID')
    home_team_name = models.CharField(max_length=200, verbose_name='홈팀명')
    home_team_logo = models.URLField(blank=True, verbose_name='홈팀 로고')
    
    away_team_id = models.CharField(max_length=100, verbose_name='원정팀 ID')
    away_team_name = models.CharField(max_length=200, verbose_name='원정팀명')
    away_team_logo = models.URLField(blank=True, verbose_name='원정팀 로고')
    
    # 경기 결과
    home_score = models.IntegerField(null=True, blank=True, verbose_name='홈팀 득점')
    away_score = models.IntegerField(null=True, blank=True, verbose_name='원정팀 득점')
    
    # 경기 상태
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name='경기 상태')
    
    # 경기장 정보
    venue = models.CharField(max_length=200, blank=True, verbose_name='경기장')
    
    # 추가 정보
    home_half_score = models.IntegerField(null=True, blank=True, verbose_name='홈팀 전반 득점')
    away_half_score = models.IntegerField(null=True, blank=True, verbose_name='원정팀 전반 득점')
    
    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '경기'
        verbose_name_plural = '경기들'
        ordering = ['-match_date']
        indexes = [
            models.Index(fields=['match_date']),
            models.Index(fields=['status']),
            models.Index(fields=['home_team_id']),
            models.Index(fields=['away_team_id']),
        ]
    
    def __str__(self):
        if self.home_score is not None and self.away_score is not None:
            return f"{self.home_team_name} {self.home_score} - {self.away_score} {self.away_team_name}"
        return f"{self.home_team_name} vs {self.away_team_name}"
    
    @property
    def is_finished(self):
        """경기 종료 여부"""
        return self.status == 'finished'
    
    @property
    def is_live(self):
        """경기 진행 중 여부"""
        return self.status == 'live'