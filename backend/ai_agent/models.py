# ai_agent/models.py

from django.db import models
from accounts.models import User


class AIConversation(models.Model):
    """AI Agent와의 대화 기록"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ai_conversations",
        verbose_name="사용자",
    )

    # 질문 분석 결과
    question = models.TextField(verbose_name="질문")
    intent = models.CharField(
        max_length=50,
        verbose_name="의도",
        choices=[
            ("경기_일정", "경기 일정"),
            ("팀_정보", "팀 정보"),
            ("선수_정보", "선수 정보"),
            ("순위_정보", "순위 정보"),
            ("분석_요청", "분석 요청"),
        ],
    )

    # 추출된 엔티티
    team_name = models.CharField(
        max_length=200, blank=True, default="", verbose_name="팀명"
    )
    player_name = models.CharField(
        max_length=200, blank=True, default="", verbose_name="선수명"
    )

    # 답변
    answer = models.TextField(verbose_name="답변")

    # 메타데이터
    search_results = models.JSONField(default=dict, verbose_name="검색 결과")

    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")

    class Meta:
        verbose_name = "AI 대화"
        verbose_name_plural = "AI 대화들"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.question[:50]}"
