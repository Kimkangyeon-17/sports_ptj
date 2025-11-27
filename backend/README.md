# Sports PTJ Backend

Django REST Framework 기반 축구 데이터 분석 API 서버

## 🚀 빠른 시작

### 1. 설치
```bash
cd backend
uv sync
```

### 2. 환경변수 설정
```bash
cp .env.example .env
# .env 파일에서 SECRET_KEY 수정
```

**SECRET_KEY 생성:**
```bash
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. 데이터베이스 & 데이터 로딩
```bash
uv run python manage.py migrate

# 데이터 로드
uv run python manage.py load_teams
uv run python manage.py load_players
uv run python manage.py load_staff
uv run python manage.py update_standings
```

### 4. 서버 실행
```bash
uv run python manage.py runserver
```

## 📡 API 엔드포인트

### 선수
- `GET /api/players/` - 선수 목록
- `GET /api/players/search/?name=son&team=Tottenham` - 선수 검색

### 팀
- `GET /api/teams/` - 팀 목록
- `GET /api/teams/{id}/players/` - 팀 소속 선수

### 감독/코치
- `GET /api/staff/` - 감독/코치 목록
- `GET /api/staff/search/?position=Manager` - 검색

### 순위표
- `GET /api/standings/` - 전체 순위표 (자동 업데이트)
- `GET /api/standings/top/?n=5` - 상위 N팀
- `GET /api/standings/bottom/` - 강등권

## 🛠 주요 명령어

```bash
# 순위표 강제 업데이트
uv run python manage.py update_standings --force

# 린팅
uv run ruff check .
uv run ruff format .

# 테스트
uv run pytest
```

## 📁 구조
```
backend/
├── players/          # 선수 API
├── teams/            # 팀, 감독, 순위표 API
├── data/             # 데이터 파일
│   ├── club/
│   ├── player_profiles/
│   └── standings/    (자동 생성)
└── manage.py
```

## 📊 데이터
- 선수: 627명
- 팀: 20개
- 스태프: 342명
- 순위표: ESPN API 자동 연동