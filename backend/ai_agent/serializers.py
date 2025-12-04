from rest_framework import serializers


class AIQuestionSerializer(serializers.Serializer):
    """AI 질문 요청"""

    question = serializers.CharField(
        required=True, max_length=500, help_text="사용자 질문"
    )


class AIAnswerSerializer(serializers.Serializer):
    """AI 답변 응답"""

    question = serializers.CharField(help_text="원본 질문")
    intent = serializers.CharField(help_text="질문 의도")
    team_name = serializers.CharField(allow_null=True, help_text="추출된 팀명")
    answer = serializers.CharField(help_text="AI 답변")
    search_results = serializers.JSONField(help_text="검색 결과 (디버깅용)")


class ConversationSerializer(serializers.Serializer):
    """대화 히스토리"""

    id = serializers.IntegerField()
    question = serializers.CharField()
    answer = serializers.CharField()
    intent = serializers.CharField()
    team_name = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()
