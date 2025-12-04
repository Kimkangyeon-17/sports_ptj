import requests
import time

BASE = "http://localhost:8000"

# 로그인
login = requests.post(
    f"{BASE}/api/accounts/login/", json={"username": "admin", "password": "admin1234"}
)
token = login.json()["access"]

# 🔥 실제 DB에 있는 선수로 테스트!
test_questions = [
    "아스날 다음 경기 언제야?",  # 경기_일정
    "리버풀 순위 알려줘",  # 순위_정보
    "Salah 정보 알려줘",  # 선수_정보 (Mohamed Salah - 리버풀)
    "맨시티 최근 폼 어때?",  # 팀_정보
    "EPL 순위표 보여줘",  # 순위_정보
    "첼시 vs 아스날 경기 분석해줘",  # 분석_요청
]

print("=" * 60)
print("🧪 다양한 질문 테스트")
print("=" * 60)

for i, question in enumerate(test_questions, 1):
    print(f"\n{i}. 질문: {question}")
    print("-" * 60)

    response = requests.post(
        f"{BASE}/api/ai/ask/",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": question},
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ 의도: {result['intent']}")
        print(f"✅ 팀명: {result.get('team_name', 'N/A')}")
        print(f"✅ 선수명: {result.get('player_name', 'N/A')}")
        print(f"\n답변 미리보기:")
        print(result["answer"][:200] + "...")
    else:
        print(f"❌ 실패: {response.status_code}")
        print(response.text)

    time.sleep(1)

print("\n" + "=" * 60)
print("✅ 모든 테스트 완료!")
print("=" * 60)
