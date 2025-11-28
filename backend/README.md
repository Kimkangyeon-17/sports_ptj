# Sports Project Backend

Django REST Framework 기반 EPL(English Premier League) 축구 정보 플랫폼 백엔드 API

## 📋 목차

- [기술 스택](#기술-스택)
- [시작하기](#시작하기)
- [데이터 로드](#데이터-로드)
- [API 명세서](#api-명세서)
- [주요 기능](#주요-기능)

---

## 🛠 기술 스택

- **Python** 3.11+
- **Django** 5.2
- **Django REST Framework** 3.16
- **SQLite** (개발용)
- **uv** (패키지 관리)
- **requests**, **pandas** (ESPN API 연동)
- **django-allauth** (소셜 로그인)
- **djangorestframework-simplejwt** (JWT 인증)

---

## 🚀 시작하기

### 1. uv 설치

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 프로젝트 클론 및 설정

```bash
# 저장소 클론
git clone <repository-url>
cd backend

# 의존성 설치
uv sync

# .env 파일 생성
cp .env.example .env
```

### 3. 환경 변수 설정

`.env` 파일을 열어서 다음 내용을 설정:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 소셜 로그인 (선택사항)
NAVER_CLIENT_ID=your-naver-client-id
NAVER_CLIENT_SECRET=your-naver-client-secret
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**SECRET_KEY 생성:**
```bash
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. 데이터베이스 마이그레이션

```bash
uv run python manage.py migrate
```

### 5. 슈퍼유저 생성

```bash
uv run python manage.py createsuperuser
```

### 6. 서버 실행

```bash
uv run python manage.py runserver
```

서버 실행 후: http://127.0.0.1:8000/api/

---

## 📊 데이터 로드

### 초기 데이터 로드 순서

프로젝트를 처음 시작할 때 다음 순서대로 데이터를 로드하세요:

```bash
# 1. 팀 데이터 로드 (20개 팀)
uv run python manage.py load_teams

# 2. 선수 데이터 로드 (627명)
uv run python manage.py load_players

# 3. 스태프 데이터 로드 (342명 - 감독, 코치 등)
uv run python manage.py load_staff

# 4. EPL 순위표 업데이트 (ESPN API)
uv run python manage.py update_standings

# 5. 경기 일정 업데이트 (ESPN API - 2025-26 시즌)
uv run python manage.py update_matches
```

### 데이터 업데이트

```bash
# 순위표 강제 업데이트
uv run python manage.py update_standings --force

# 경기 일정 강제 업데이트
uv run python manage.py update_matches --force
```

---

## 📖 API 명세서

### Base URL
```
http://127.0.0.1:8000/api/
```

---

## 🔐 인증 (Authentication)

### 회원가입
```http
POST /api/accounts/register/
```

**Request Body:**
```json
{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123",
    "nickname": "테스터"
}
```

**Response:**
```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "nickname": "테스터"
}
```

---

### 로그인
```http
POST /api/accounts/login/
```

**Request Body:**
```json
{
    "username": "testuser",
    "password": "testpass123"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "nickname": "테스터"
    }
}
```

---

### 로그아웃
```http
POST /api/accounts/logout/
Authorization: Bearer {access_token}
```

---

### 사용자 정보 조회
```http
GET /api/accounts/user/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "nickname": "테스터",
    "favorite_teams": [
        {
            "team_id": "359",
            "team_name": "Arsenal",
            "league": ""
        }
    ],
    "favorite_teams_count": 1
}
```

---

### 토큰 갱신
```http
POST /api/accounts/token/refresh/
```

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 소셜 로그인

#### 네이버 로그인
```http
GET /api/accounts/naver/login/
```
브라우저에서 접속하면 네이버 로그인 페이지로 리다이렉트

#### 구글 로그인
```http
GET /api/accounts/google/login/
```
브라우저에서 접속하면 구글 로그인 페이지로 리다이렉트

---

## ⚽ 팀 (Teams)

### 팀 목록 조회
```http
GET /api/teams/
```

**Response:**
```json
[
    {
        "team_id": "359",
        "team_name": "Arsenal",
        "league": ""
    }
]
```

---

### 팀 상세 정보
```http
GET /api/teams/{id}/
```

---

### 팀 검색
```http
GET /api/teams/search/?name=Arsenal&league=Premier League
```

**Query Parameters:**
- `name`: 팀 이름 (부분 일치)
- `league`: 리그 이름

---

### 팀 소속 선수 목록
```http
GET /api/teams/{id}/players/
```

---

## 👥 선수 (Players)

### 선수 목록 조회
```http
GET /api/players/
```

**Response:**
```json
{
    "count": 627,
    "results": [
        {
            "player_id": "123",
            "name": "Bukayo Saka",
            "position": "Forward",
            "jersey_number": "7",
            "team_name": "Arsenal"
        }
    ]
}
```

---

### 선수 상세 정보
```http
GET /api/players/{id}/
```

---

### 선수 검색
```http
GET /api/players/search/?name=Saka&team=Arsenal&position=Forward&nationality=England
```

**Query Parameters:**
- `name`: 선수 이름 (부분 일치)
- `team`: 팀 이름
- `position`: 포지션
- `nationality`: 국적

---

## 👔 감독/코치 (Staff)

### 스태프 목록 조회
```http
GET /api/staff/
```

---

### 스태프 검색
```http
GET /api/staff/search/?name=Arteta&team=Arsenal&position=Manager
```

**Query Parameters:**
- `name`: 이름 (부분 일치)
- `team`: 팀 이름
- `position`: 직책

---

## 🏆 순위표 (Standings)

### EPL 순위표 조회
```http
GET /api/standings/
```

**Response:**
```json
[
    {
        "rank": 1,
        "team_name": "Liverpool",
        "team_logo": "https://...",
        "points": 45,
        "matches_played": 17,
        "wins": 14,
        "draws": 3,
        "losses": 0,
        "goals_for": 42,
        "goals_against": 15,
        "goal_difference": 27
    }
]
```

**Note:** API 호출 시 자동으로 오늘 날짜 데이터가 없으면 업데이트됩니다.

---

### 상위 N팀 조회
```http
GET /api/standings/top/?n=5
```

---

### 하위 N팀 조회 (강등권)
```http
GET /api/standings/bottom/?n=3
```

---

### 순위표 강제 업데이트
```http
POST /api/standings/force_update/
```

---

## 📅 경기 일정 (Matches)

### 전체 경기 목록
```http
GET /api/matches/
```

**Response:**
```json
{
    "count": 90,
    "results": [
        {
            "match_id": "740718",
            "match_date": "2025-11-29T15:00:00Z",
            "home_team_name": "Brentford",
            "away_team_name": "Burnley",
            "home_score": 0,
            "away_score": 0,
            "status": "scheduled",
            "is_finished": false,
            "is_live": false
        }
    ]
}
```

---

### 경기 상세 정보
```http
GET /api/matches/{match_id}/
```

---

### 예정된 경기
```http
GET /api/matches/upcoming/
```

최대 10개의 예정된 경기를 날짜순으로 반환

---

### 진행 중인 경기
```http
GET /api/matches/live/
```

---

### 종료된 경기
```http
GET /api/matches/finished/
```

최대 20개의 종료된 경기를 최신순으로 반환

---

### 날짜별 경기 조회
```http
GET /api/matches/by_date/?date=2025-11-29
```

**Query Parameters:**
- `date`: 날짜 (YYYY-MM-DD 형식)

---

### 팀별 경기 조회
```http
GET /api/matches/by_team/?team_id=359
GET /api/matches/by_team/?team_name=Arsenal
```

**Query Parameters:**
- `team_id`: 팀 ID
- `team_name`: 팀 이름 (부분 일치)

---

### 라운드별 경기 조회
```http
GET /api/matches/by_matchday/?matchday=15
```

**Query Parameters:**
- `matchday`: 라운드 번호

---

### 경기 데이터 강제 업데이트
```http
POST /api/matches/force_update/
```

---

## ⭐ 응원 팀 (Favorite Teams)

> **인증 필요:** 모든 응원 팀 API는 JWT 토큰이 필요합니다.

### 내 응원 팀 목록
```http
GET /api/accounts/favorite-teams/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
    "count": 3,
    "max_count": 3,
    "teams": [
        {
            "team_id": "359",
            "team_name": "Arsenal",
            "league": ""
        }
    ]
}
```

---

### 응원 팀 추가
```http
POST /api/accounts/favorite-teams/add/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
    "team_id": "359"
}
```

**제약사항:**
- 최대 3개까지만 추가 가능
- 중복 추가 불가

---

### 응원 팀 제거
```http
DELETE /api/accounts/favorite-teams/remove/{team_id}/
Authorization: Bearer {access_token}
```

---

### 특정 응원 팀 경기 일정
```http
GET /api/accounts/favorite-teams/{team_id}/matches/
Authorization: Bearer {access_token}
```

최대 20개의 경기를 최신순으로 반환

---

### 모든 응원 팀 경기 일정
```http
GET /api/accounts/favorite-teams/matches/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
    "teams": [...],
    "upcoming_count": 20,
    "past_count": 20,
    "upcoming_matches": [...],
    "past_matches": [...]
}
```

---

### 응원 팀 예정된 경기만
```http
GET /api/accounts/favorite-teams/matches/upcoming/
Authorization: Bearer {access_token}
```

**정렬:** 가까운 미래부터 오름차순 (최대 20개)

---

### 응원 팀 지난 경기만
```http
GET /api/accounts/favorite-teams/matches/past/
Authorization: Bearer {access_token}
```

**정렬:** 최근부터 내림차순 (최대 20개)

---

## 📂 프로젝트 구조

```
backend/
├── config/                 # 프로젝트 설정
│   ├── settings.py
│   └── urls.py
├── accounts/              # 사용자 인증
│   ├── models.py         # User 모델
│   ├── views.py          # 회원가입, 로그인, 응원 팀
│   └── serializers.py
├── teams/                 # 팀 관리
│   ├── models.py         # Team, Staff, TeamStanding
│   ├── views.py
│   └── management/commands/
│       ├── load_teams.py
│       ├── load_staff.py
│       └── update_standings.py
├── players/               # 선수 관리
│   ├── models.py         # Player
│   ├── views.py
│   └── management/commands/
│       └── load_players.py
├── matches/               # 경기 일정
│   ├── models.py         # Match
│   ├── views.py
│   └── management/commands/
│       └── update_matches.py
├── ai_analysis/          # AI 분석 (예정)
├── data/                 # 데이터 파일
│   ├── club/            # 팀, 선수 CSV
│   ├── player_profiles/ # 선수 프로필 JSON
│   └── standings/       # 순위표 CSV
└── db.sqlite3           # SQLite 데이터베이스
```

---

## 🔑 주요 기능

### 1. 인증 시스템
- ✅ JWT 기반 토큰 인증
- ✅ 회원가입/로그인/로그아웃
- ✅ 소셜 로그인 (네이버, 구글)
- ✅ 사용자 프로필 관리

### 2. 응원 팀 관리
- ✅ 최대 3개 팀 선택
- ✅ 응원 팀 추가/제거
- ✅ 응원 팀 경기 일정 조회
- ✅ 예정/지난 경기 구분

### 3. EPL 데이터
- ✅ 20개 팀 정보
- ✅ 627명 선수 정보
- ✅ 342명 스태프 정보 (감독, 코치 등)
- ✅ 실시간 순위표 (ESPN API)

### 4. 경기 일정
- ✅ 2025-26 시즌 전체 일정
- ✅ 예정/진행중/종료 경기 구분
- ✅ 팀별, 날짜별, 라운드별 검색
- ✅ 자동 업데이트

---

## 🐛 개발 도구

### 코드 린팅
```bash
uv run ruff check .
uv run ruff format .
```

### Django Admin
```
http://127.0.0.1:8000/admin/
```

슈퍼유저 계정으로 로그인하여 데이터 관리

---

## 📝 환경 변수

| 변수명 | 설명 | 필수 여부 |
|--------|------|-----------|
| SECRET_KEY | Django 시크릿 키 | ✅ |
| DEBUG | 디버그 모드 | ✅ |
| ALLOWED_HOSTS | 허용 호스트 | ✅ |
| NAVER_CLIENT_ID | 네이버 로그인 클라이언트 ID | ❌ |
| NAVER_CLIENT_SECRET | 네이버 로그인 시크릿 | ❌ |
| GOOGLE_CLIENT_ID | 구글 로그인 클라이언트 ID | ❌ |
| GOOGLE_CLIENT_SECRET | 구글 로그인 시크릿 | ❌ |

---

## 📊 데이터 소스

- **ESPN API**: 경기 일정, 순위표
- **CSV 파일**: 팀, 선수, 스태프 기본 정보
- **Wikipedia API**: 선수 프로필 정보

---

## 📄 라이선스

This project is licensed under the MIT License.