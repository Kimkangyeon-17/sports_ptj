"""
질문 분석 Agent
- 사용자 질문의 의도를 파악
- 팀명, 선수명 등 엔티티 추출
"""

import os
from dotenv import load_dotenv
from typing import TypedDict
import json
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_upstage import ChatUpstage

# 환경변수 로드
load_dotenv()


# 상태 정의
class AnalysisState(TypedDict):
    """질문 분석 Agent의 상태"""

    question: str
    intent: str  # 의도
    team_name: str | None  # 팀명
    player_name: str | None  # 선수명
    date_range: str | None  # 시간 범위
    urgency: str  # 긴급도


class SportsQuestionAnalyzer:
    """스포츠 질문 분석 Agent"""

    def __init__(self):
        # Solar Mini: 빠르고 저렴한 분류 작업용
        self.llm = ChatUpstage(
            model="solar-1-mini-chat", temperature=0  # 분류는 일관성이 중요
        )

        # 프롬프트 템플릿
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """당신은 EPL(English Premier League) 축구 정보 분석 전문가입니다.
                사용자의 질문을 분석하여 의도를 파악하고 필요한 정보를 추출하세요.
                
                # 의도 분류 (5가지)
                1. 경기_일정: 경기 일정, 다음 경기, 언제 경기하는지 등
                   예: "아스날 다음 경기 언제야?", "이번 주말 경기 일정"
                
                2. 팀_정보: 팀 순위, 성적, 최근 폼 등
                   예: "리버풀 요즘 어때?", "맨시티 순위가 어떻게 돼?"
                
                3. 선수_정보: 선수 정보, 스탯, 포지션 등
                   예: "손흥민 정보 알려줘", "살라 골 몇 개?"
                
                4. 순위_정보: EPL 순위표 전체 또는 상위/하위권
                   예: "EPL 순위 알려줘", "강등권 팀은?"
                
                5. 분석_요청: 경기 분석, 예측, 팀/선수 비교 등
                   예: "아스날 vs 첼시 누가 이길까?", "리버풀 우승 가능성"
                
                # 엔티티 추출
                - team_name: 질문에 나온 팀 이름 (예: "아스날", "리버풀")
                - player_name: 질문에 나온 선수 이름 (예: "손흥민", "살라")
                - date_range: 시간 관련 표현을 다음 중 하나로 분류
                  * "recent": 최근, 지난, 이전
                  * "upcoming": 다음, 앞으로, 예정
                  * null: 시간 언급 없음
                
                # 출력 형식 (반드시 JSON만 출력)
                {{
                  "intent": "경기_일정 | 팀_정보 | 선수_정보 | 순위_정보 | 분석_요청",
                  "team_name": "팀 이름 또는 null",
                  "player_name": "선수 이름 또는 null",
                  "date_range": "recent | upcoming | null",
                  "urgency": "보통"
                }}
                
                주의: JSON 형식만 출력하세요. 다른 설명은 불필요합니다.
                """,
                ),
                ("user", "질문: {question}"),
            ]
        )

        # LCEL 체인
        self.chain = self.prompt | self.llm

    def _extract_json(self, text: str) -> dict:
        """
        LLM 응답에서 JSON 추출

        Args:
            text: LLM 응답 텍스트

        Returns:
            파싱된 JSON 딕셔너리
        """
        # 1. 코드 블록 제거
        if "```json" in text:
            match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
            if match:
                text = match.group(1)
        elif "```" in text:
            match = re.search(r"```\s*(\{.*?\})\s*```", text, re.DOTALL)
            if match:
                text = match.group(1)

        # 2. JSON 객체 추출
        match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)

        # 3. 실패 시 예외
        raise ValueError("JSON을 찾을 수 없습니다.")

    def analyze(self, state: AnalysisState) -> AnalysisState:
        """
        질문 분석 실행

        Args:
            state: 현재 상태 (question 포함)

        Returns:
            분석 결과가 추가된 상태
        """
        question = state["question"]

        print(f"\n🔍 질문 분석 중: {question}")

        try:
            # LLM 호출
            response = self.chain.invoke({"question": question})

            # JSON 추출 및 파싱
            result = self._extract_json(response.content)

            print(f"   ✅ 의도: {result.get('intent')}")
            print(f"   ✅ 팀명: {result.get('team_name')}")
            print(f"   ✅ 선수명: {result.get('player_name')}")
            print(f"   ✅ 시간: {result.get('date_range')}")

            # 상태 업데이트
            return {
                "question": question,
                "intent": result.get("intent", "분석_요청"),
                "team_name": result.get("team_name"),
                "player_name": result.get("player_name"),
                "date_range": result.get("date_range"),
                "urgency": result.get("urgency", "보통"),
            }

        except Exception as e:
            print(f"   ⚠️  분석 실패: {e}")
            # 기본값 반환
            return {
                "question": question,
                "intent": "분석_요청",
                "team_name": None,
                "player_name": None,
                "date_range": None,
                "urgency": "보통",
            }


# --- 테스트 코드 ---
if __name__ == "__main__":
    analyzer = SportsQuestionAnalyzer()

    # 테스트 케이스
    test_questions = [
        "아스날 다음 경기 언제야?",
        "리버풀 요즘 어때?",
        "손흥민 골 몇 개?",
        "EPL 순위 알려줘",
        "아스날 vs 첼시 누가 이길까?",
    ]

    print("=" * 60)
    print("SportsQuestionAnalyzer 테스트")
    print("=" * 60)

    for i, question in enumerate(test_questions, 1):
        print(f"\n[테스트 {i}/{len(test_questions)}]")

        state = {
            "question": question,
            "intent": "",
            "team_name": None,
            "player_name": None,
            "date_range": None,
            "urgency": "보통",
        }

        result = analyzer.analyze(state)
        print(f"\n결과: {result}")
        print("-" * 60)

    print("\n✨ 테스트 완료!")
