# ai_agent/agents/answer_generator.py

"""
답변 생성 Agent
- 검색된 데이터를 바탕으로 자연스러운 답변 생성
- Upstage Solar LLM 사용
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Dict, Any
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_upstage import ChatUpstage

# 환경변수 로드
load_dotenv()


# 상태 정의
class AnswerState(TypedDict):
    """답변 생성 Agent의 상태"""

    question: str
    intent: str
    team_name: str | None
    player_name: str | None
    date_range: str | None
    urgency: str
    search_results: Dict[str, Any]
    answer: str  # 생성된 답변


class SportsAnswerGenerator:
    """스포츠 데이터 기반 답변 생성 Agent"""

    def __init__(self):
        # Solar Pro: 답변 생성용 (더 똑똑함)
        self.llm = ChatUpstage(model="solar-pro", temperature=0.3)  # 약간의 창의성

        # 답변 생성 프롬프트
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """당신은 EPL 축구 전문 AI 어시스턴트입니다.
        주어진 데이터를 바탕으로 정확하고 친절하게 답변하세요.

        # 답변 스타일
        - 자연스러운 한국어 사용
        - 이모지 적절히 활용 (⚽ 🏆 📊 등)
        - 핵심 정보 먼저, 상세 정보는 그 다음
        - 데이터가 없으면 솔직하게 말하기

        # 답변 형식
        📌 요약: (한 줄로 핵심 답변)

        📊 상세 정보:
        (구조화된 데이터, 목록 형태)

        💡 추가 정보:
        (참고할만한 팁이나 분석)

        # 순위표 답변 시 중요 규칙
        - 전체 순위표 요청 시: **상위 5개 팀 + 하위 3개 팀**을 반드시 표로 보여주세요
        - 표 형식: | 순위 | 팀명 | (마크다운 테이블)
        - 상위 5개 팀 → 한 줄 띄우기 → 하위 3개 팀 순서로 작성
        - 예시:
        | 순위 | 팀명 |
        |------|------|
        | 1 | Arsenal |
        | 2 | Man City |
        ...
        | 18 | Burnley |
        | 19 | Leeds |
        | 20 | Sunderland |

        # 주의사항
        - 데이터에 없는 내용은 추측하지 않기
        - 날짜/시간은 한국 시간으로 변환해서 설명
        - 경기 결과는 점수와 함께 명확히 표시
        - 순위표는 상위 5개 + 하위 3개를 **반드시** 모두 보여주기
        """,
                ),
                (
                    "user",
                    """질문: {question}

        의도: {intent}
        팀명: {team_name}
        선수명: {player_name}

        검색된 데이터:
        {search_results}

        위 데이터를 바탕으로 답변을 생성하세요.""",
                ),
            ]
        )

        # LCEL 체인
        self.chain = self.prompt | self.llm

    def generate(self, state: AnswerState) -> AnswerState:
        """
        답변 생성

        Args:
            state: 현재 상태 (검색 결과 포함)

        Returns:
            답변이 추가된 상태
        """
        question = state["question"]
        intent = state["intent"]
        search_results = state.get("search_results", {})

        print(f"\n💬 답변 생성 중...")
        print(f"   질문: {question}")
        print(f"   의도: {intent}")

        # 검색 결과가 없는 경우
        if not search_results or all(not v for v in search_results.values()):
            return {
                **state,
                "answer": self._generate_no_data_response(question, intent),
            }

        try:
            # 검색 결과를 JSON 문자열로 변환
            search_results_str = json.dumps(
                search_results,
                ensure_ascii=False,
                indent=2,
                default=str,  # datetime 등을 문자열로 변환
            )

            # LLM 호출
            response = self.chain.invoke(
                {
                    "question": question,
                    "intent": intent,
                    "team_name": state.get("team_name", "없음"),
                    "player_name": state.get("player_name", "없음"),
                    "search_results": search_results_str,
                }
            )

            answer = response.content
            print(f"   ✅ 답변 생성 완료 ({len(answer)} 글자)")

            return {**state, "answer": answer}

        except Exception as e:
            print(f"   ⚠️  답변 생성 오류: {e}")
            return {**state, "answer": "죄송합니다. 답변 생성 중 오류가 발생했습니다."}

    def _generate_no_data_response(self, question: str, intent: str) -> str:
        """데이터가 없을 때 기본 답변"""
        responses = {
            "경기_일정": "죄송합니다. 해당 팀의 경기 일정을 찾을 수 없습니다. 팀 이름을 다시 확인해주세요.",
            "팀_정보": "죄송합니다. 해당 팀의 정보를 찾을 수 없습니다. 팀 이름을 정확히 입력해주세요.",
            "선수_정보": "죄송합니다. 해당 선수의 정보를 찾을 수 없습니다. 선수 이름을 확인해주세요.",
            "순위_정보": "죄송합니다. 현재 순위 정보를 가져올 수 없습니다. 잠시 후 다시 시도해주세요.",
            "분석_요청": "죄송합니다. 요청하신 정보를 찾을 수 없습니다. 질문을 다시 확인해주세요.",
        }

        return responses.get(intent, "죄송합니다. 요청하신 정보를 찾을 수 없습니다.")
