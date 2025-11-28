from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    UserProfileView,
    user_info,
    # kakao_login,
    # kakao_callback,
    naver_login,
    naver_callback,
    google_login,
    google_callback,
    my_favorite_teams,
    add_favorite_team,
    remove_favorite_team,
    favorite_team_matches,
    all_favorite_matches,
    upcoming_favorite_matches,
    past_favorite_matches,
)

urlpatterns = [
    # 기본 인증 (dj-rest-auth)
    path("", include("dj_rest_auth.urls")),  # login, logout, password 등
    # 회원가입
    path("register/", RegisterView.as_view(), name="register"),
    # JWT 토큰
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # 사용자 정보
    path("user/", user_info, name="user_info"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    # 카카오 로그인
    # path("kakao/login/", kakao_login, name="kakao_login"),
    # path("kakao/callback/", kakao_callback, name="kakao_callback"),
    # 네이버 로그인
    path("naver/login/", naver_login, name="naver_login"),
    path("naver/callback/", naver_callback, name="naver_callback"),
    # 구글 로그인
    path("google/login/", google_login, name="google_login"),
    path("google/callback/", google_callback, name="google_callback"),
    # 응원 팀 관리
    path("favorite-teams/", my_favorite_teams, name="my_favorite_teams"),
    path("favorite-teams/add/", add_favorite_team, name="add_favorite_team"),
    path(
        "favorite-teams/remove/<str:team_id>/",
        remove_favorite_team,
        name="remove_favorite_team",
    ),
    path(
        "favorite-teams/<str:team_id>/matches/",
        favorite_team_matches,
        name="favorite_team_matches",
    ),
    path("favorite-teams/matches/", all_favorite_matches, name="all_favorite_matches"),
    path(
        "favorite-teams/matches/upcoming/",
        upcoming_favorite_matches,
        name="upcoming_favorite_matches",
    ),
    path(
        "favorite-teams/matches/past/",
        past_favorite_matches,
        name="past_favorite_matches",
    ),
]
