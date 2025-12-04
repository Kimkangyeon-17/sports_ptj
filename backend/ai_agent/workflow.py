"""
AI Agent Workflow
- LangGraph를 사용한 멀티 에이전트 통합
- Question Analyzer → Data Search → Answer Generator
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

from ai_agent.agents.question_analyzer import SportsQuestionAnalyzer
from ai_agent.agents.data_search_agent import SportsDataSearchAgent
from ai_agent.agents.answer_generator import SportsAnswerGenerator


# 전체 워크플로우 상태
class WorkflowState(TypedDict):
    """AI Workflow의 전체 상태"""

    # 입력
    question: str

    # 질문 분석 결과
    intent: str
    team_name: str | None
    player_name: str | None
    date_range: str | None
    urgency: str

    # 검색 결과
    search_results: dict

    # 최종 답변
    answer: str


class SportsAIWorkflow:
    """스포츠 AI Workflow"""

    def __init__(self):
        # Agent들 초기화
        self.question_analyzer = SportsQuestionAnalyzer()
        self.data_search = SportsDataSearchAgent()
        self.answer_generator = SportsAnswerGenerator()

        # Workflow 그래프 생성
        self.app = self._create_workflow()

    def _create_workflow(self):
        """LangGraph 워크플로우 생성"""

        # 워크플로우 그래프
        workflow = StateGraph(WorkflowState)

        # 노드 추가
        workflow.add_node("analyze", self.question_analyzer.analyze)
        workflow.add_node("search", self.data_search.search_with_metadata)
        workflow.add_node("generate", self.answer_generator.generate)

        # 엣지 정의 (순차 실행)
        workflow.add_edge("analyze", "search")
        workflow.add_edge("search", "generate")
        workflow.add_edge("generate", END)

        # 시작점 설정
        workflow.set_entry_point("analyze")

        # 컴파일
        return workflow.compile()

    def run(self, question: str) -> dict:  # 👈 반환 타입을 dict로 명시
        """
        워크플로우 실행

        Args:
            question: 사용자 질문

        Returns:
            최종 상태 (답변 포함) - None 값 방어 처리됨
        """
        # 초기 상태
        initial_state = {
            "question": question,
            "intent": "",
            "team_name": "",  # 👈 빈 문자열로 시작
            "player_name": "",  # 👈 빈 문자열로 시작
            "date_range": None,
            "urgency": "보통",
            "search_results": {},
            "answer": "",
        }

        print(f"\n{'='*60}")
        print(f"🤖 Sports AI Workflow 시작")
        print(f"{'='*60}")
        print(f"질문: {question}\n")

        try:
            # 워크플로우 실행
            final_state = self.app.invoke(initial_state)

            print(f"\n{'='*60}")
            print(f"✅ Workflow 완료!")
            print(f"{'='*60}\n")

            # 🔥 None 값 방어 처리
            return {
                "question": final_state.get("question", question),
                "intent": final_state.get("intent", "알 수 없음"),
                "team_name": final_state.get("team_name")
                or "",  # 👈 None이면 빈 문자열
                "player_name": final_state.get("player_name")
                or "",  # 👈 None이면 빈 문자열
                "date_range": final_state.get("date_range"),
                "urgency": final_state.get("urgency", "보통"),
                "search_results": final_state.get("search_results", {}),
                "answer": final_state.get("answer", "답변을 생성할 수 없습니다."),
            }

        except Exception as e:
            print(f"\n❌ Workflow 오류: {e}")
            import traceback

            traceback.print_exc()

            # 오류 시 기본 답변
            return {
                "question": question,
                "intent": "오류",
                "team_name": "",
                "player_name": "",
                "date_range": None,
                "urgency": "보통",
                "search_results": {},
                "answer": f"죄송합니다. 처리 중 오류가 발생했습니다: {str(e)}",
            }


# 전역 인스턴스 (재사용)
_workflow_instance = None


def get_workflow() -> SportsAIWorkflow:
    """
    Workflow 싱글톤 인스턴스 가져오기
    (서버 시작 시 한 번만 초기화)
    """
    global _workflow_instance

    if _workflow_instance is None:
        print("🔄 Sports AI Workflow 초기화 중...")
        _workflow_instance = SportsAIWorkflow()
        print("✅ Workflow 준비 완료!\n")

    return _workflow_instance
