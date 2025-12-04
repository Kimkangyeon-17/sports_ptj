from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from ai_agent.workflow import get_workflow
from ai_agent.serializers import AIQuestionSerializer, AIAnswerSerializer
from ai_agent.models import AIConversation


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ask_ai(request):
    """
    AI에게 질문하기

    POST /api/ai/ask/
    {
        "question": "아스날 다음 경기 언제야?"
    }
    """
    # 요청 검증
    serializer = AIQuestionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    question = serializer.validated_data["question"]

    try:
        # Workflow 실행
        workflow = get_workflow()
        result = workflow.run(question)

        # DB에 저장
        conversation = AIConversation.objects.create(
            user=request.user,
            question=result["question"],
            intent=result["intent"],
            team_name=result.get("team_name", ""),
            player_name=result.get("player_name", ""),
            answer=result["answer"],
            search_results=result.get("search_results", {}),
        )

        # 🔥 응답 (player_name 추가!)
        response_data = {
            "question": result["question"],
            "intent": result["intent"],
            "team_name": result.get("team_name"),
            "player_name": result.get("player_name"),
            "answer": result["answer"],
            "search_results": result.get("search_results", {}),
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback

        traceback.print_exc()

        return Response(
            {"error": "처리 중 오류가 발생했습니다.", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def conversation_history(request):
    """
    내 대화 히스토리 조회

    GET /api/ai/history/?limit=10
    """
    limit = int(request.query_params.get("limit", 20))

    conversations = AIConversation.objects.filter(user=request.user).order_by(
        "-created_at"
    )[:limit]

    data = [
        {
            "id": conv.id,
            "question": conv.question,
            "answer": conv.answer,
            "intent": conv.intent,
            "team_name": conv.team_name,
            "player_name": conv.player_name,
            "created_at": conv.created_at,
        }
        for conv in conversations
    ]

    return Response({"count": len(data), "results": data})


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_conversation(request, conversation_id):
    """
    대화 삭제

    DELETE /api/ai/history/<id>/
    """
    try:
        conversation = AIConversation.objects.get(id=conversation_id, user=request.user)
        conversation.delete()

        return Response(
            {"message": "대화가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT
        )

    except AIConversation.DoesNotExist:
        return Response(
            {"error": "대화를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    AI Agent 헬스 체크

    GET /api/ai/health/
    """
    try:
        workflow = get_workflow()
        return Response({"status": "healthy", "message": "AI Agent is running"})
    except Exception as e:
        return Response(
            {"status": "unhealthy", "error": str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
