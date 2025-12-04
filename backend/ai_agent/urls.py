from django.urls import path
from . import views

urlpatterns = [
    # AI 질문
    path("ask/", views.ask_ai, name="ask_ai"),
    # 대화 히스토리
    path("history/", views.conversation_history, name="conversation_history"),
    path(
        "history/<int:conversation_id>/",
        views.delete_conversation,
        name="delete_conversation",
    ),
    # 헬스 체크
    path("health/", views.health_check, name="ai_health_check"),
]
