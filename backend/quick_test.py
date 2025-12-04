# backend/quick_test.py

import requests
import time

BASE = "http://localhost:8000"

print("=" * 60)
print("🧪 빠른 테스트")
print("=" * 60)

# 서버 대기
print("\n⏳ 서버 대기 중...")
time.sleep(2)

# Health Check
print("\n1️⃣ Health Check...")
try:
    health = requests.get(f"{BASE}/api/ai/health/", timeout=5)
    print(f"✅ 서버 작동: {health.json()}")
except Exception as e:
    print(f"❌ 서버 오류: {e}")
    print("\n서버가 실행 중인가요?")
    print("명령어: uv run python manage.py runserver")
    exit(1)

# 로그인
print("\n2️⃣ 로그인...")
login = requests.post(
    f"{BASE}/api/accounts/login/", json={"username": "admin", "password": "admin1234"}
)

if login.status_code != 200:
    print(f"❌ 로그인 실패: {login.text}")
    exit(1)

token = login.json()["access"]
print(f"✅ 토큰: {token[:30]}...")

# AI 질문
print("\n3️⃣ AI 질문...")
ai = requests.post(
    f"{BASE}/api/ai/ask/",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={"question": "아스날 다음 경기 언제야?"},
)

if ai.status_code == 200:
    result = ai.json()
    print(f"✅ 성공!")
    print(f"\n질문: {result['question']}")
    print(f"의도: {result['intent']}")
    print(f"팀명: {result['team_name']}")
    print(f"\n답변 미리보기:")
    print(result["answer"][:200] + "...")
else:
    print(f"❌ 실패 ({ai.status_code})")
    print(ai.text)

print("\n" + "=" * 60)
print("✅ 테스트 완료!")
print("=" * 60)
