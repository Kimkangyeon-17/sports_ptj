# Sports PTJ Backend

Django REST Framework 기반 축구 데이터 분석 API 서버

## 🚀 주요 기능

### 🔍 데이터 검색
- **선수 검색**: 이름, 팀, 포지션, 국적으로 검색
- **팀 검색**: 팀명, 리그로 검색
- **감독/코치 검색**: 이름, 팀, 포지션, 국적으로 검색

### 📊 순위표
- **EPL 순위표**: ESPN API 자동 연동
- **실시간 업데이트**: 하루 1회 자동 업데이트
- **상위/하위 팀 조회**: 챔피언스리그, 강등권 팀 조회

## 🛠 기술 스택

- **Python**: 3.11+
- **Django**: 5.2
- **Django REST Framework**: 3.16
- **Database**: SQLite (개발) / PostgreSQL (프로덕션)
- **패키지 관리**: uv

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
uv run python manage.py load_teams # 팀 데이터 로드
uv run python manage.py load_players # 선수 데이터 로드
uv run python manage.py load_staff # 감독/코치 데이터 로드
uv run python manage.py update_standings # EPL 순위표 업데이트
```

### 4. 서버 실행
```bash
uv run python manage.py runserver
```

## 📡 API 엔드포인트

### 선수 (Players)
```
GET  /api/players/                     # 선수 목록
GET  /api/players/{id}/                # 선수 상세
GET  /api/players/search/              # 선수 검색
     ?name=손흥민                       # 이름으로 검색
     &team=Tottenham                   # 팀으로 검색
     &position=Forward                 # 포지션으로 검색
     &nationality=Korea                # 국적으로 검색
```

### 팀 (Teams)
```
GET  /api/teams/                       # 팀 목록
GET  /api/teams/{id}/                  # 팀 상세
GET  /api/teams/{id}/players/          # 팀 소속 선수 목록
GET  /api/teams/search/                # 팀 검색
     ?name=Arsenal                     # 팀명으로 검색
     &league=Premier                   # 리그로 검색
```

### 감독/코치 (Staff)
```
GET  /api/staff/                       # 감독/코치 목록
GET  /api/staff/{id}/                  # 감독/코치 상세
GET  /api/staff/search/                # 감독/코치 검색
     ?name=Arteta                      # 이름으로 검색
     &team=Arsenal                     # 팀으로 검색
     &position=Manager                 # 포지션으로 검색
```

### 순위표 (Standings)
```
GET  /api/standings/                   # 전체 순위표
GET  /api/standings/{id}/              # 특정 팀 순위
GET  /api/standings/top/               # 상위 5팀
     ?n=10                             # 상위 N팀
GET  /api/standings/bottom/            # 하위 3팀 (강등권)
     ?n=5                              # 하위 N팀
POST /api/standings/force_update/      # 강제 업데이트
```

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

