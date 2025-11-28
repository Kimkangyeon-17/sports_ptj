from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
import requests
import os
from .serializers import UserSerializer, UserRegisterSerializer, FavoriteTeamSerializer
from teams.models import Team, TeamStanding
from matches.models import Match

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """회원가입 API"""

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """사용자 프로필 조회/수정 API"""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    """현재 로그인한 사용자 정보"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# ========================================
# 소셜 로그인 Views
# ========================================


def get_tokens_for_user(user):
    """사용자에 대한 JWT 토큰 생성"""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# @api_view(["GET"])
# @permission_classes([AllowAny])
# def kakao_login(request):
#     """카카오 로그인 페이지로 리다이렉트"""
#     kakao_api_key = os.getenv("KAKAO_REST_API_KEY")
#     redirect_uri = os.getenv("KAKAO_REDIRECT_URI")

#     kakao_auth_url = (
#         f"https://kauth.kakao.com/oauth/authorize"
#         f"?client_id={kakao_api_key}"
#         f"&redirect_uri={redirect_uri}"
#         f"&response_type=code"
#     )
#     return redirect(kakao_auth_url)


# @api_view(["GET"])
# @permission_classes([AllowAny])
# def kakao_callback(request):
#     """카카오 로그인 콜백"""
#     code = request.GET.get("code")

#     # 1. 액세스 토큰 받기
#     token_url = "https://kauth.kakao.com/oauth/token"
#     token_data = {
#         "grant_type": "authorization_code",
#         "client_id": os.getenv("KAKAO_REST_API_KEY"),
#         "redirect_uri": os.getenv("KAKAO_REDIRECT_URI"),
#         "code": code,
#     }

#     token_response = requests.post(token_url, data=token_data)
#     token_json = token_response.json()
#     access_token = token_json.get("access_token")

#     # 2. 사용자 정보 받기
#     user_info_url = "https://kapi.kakao.com/v2/user/me"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     user_response = requests.get(user_info_url, headers=headers)
#     user_json = user_response.json()

#     kakao_id = user_json.get("id")
#     kakao_account = user_json.get("kakao_account", {})
#     email = kakao_account.get("email", f"kakao_{kakao_id}@kakao.com")
#     nickname = kakao_account.get("profile", {}).get(
#         "nickname", f"kakao_user_{kakao_id}"
#     )
#     profile_image = kakao_account.get("profile", {}).get("profile_image_url", "")

#     # 3. 사용자 생성 또는 가져오기
#     user, created = User.objects.get_or_create(
#         social_provider="kakao",
#         social_id=str(kakao_id),
#         defaults={
#             "username": f"kakao_{kakao_id}",
#             "email": email,
#             "nickname": nickname,
#             "profile_image": profile_image,
#         },
#     )

#     # 4. JWT 토큰 발급
#     tokens = get_tokens_for_user(user)

#     return Response(
#         {
#             "message": "카카오 로그인 성공",
#             "tokens": tokens,
#             "user": UserSerializer(user).data,
#         }
#     )


@api_view(["GET"])
@permission_classes([AllowAny])
def naver_login(request):
    """네이버 로그인 페이지로 리다이렉트"""
    client_id = os.getenv("NAVER_CLIENT_ID")
    redirect_uri = os.getenv("NAVER_REDIRECT_URI")
    state = "random_state_string"  # 보안을 위한 랜덤 문자열

    naver_auth_url = (
        f"https://nid.naver.com/oauth2.0/authorize"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
    )
    return redirect(naver_auth_url)


@api_view(["GET"])
@permission_classes([AllowAny])
def naver_callback(request):
    """네이버 로그인 콜백"""
    code = request.GET.get("code")
    state = request.GET.get("state")

    # 1. 액세스 토큰 받기
    token_url = "https://nid.naver.com/oauth2.0/token"
    token_data = {
        "grant_type": "authorization_code",
        "client_id": os.getenv("NAVER_CLIENT_ID"),
        "client_secret": os.getenv("NAVER_CLIENT_SECRET"),
        "code": code,
        "state": state,
    }

    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()
    access_token = token_json.get("access_token")

    # 2. 사용자 정보 받기
    user_info_url = "https://openapi.naver.com/v1/nid/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(user_info_url, headers=headers)
    user_json = user_response.json()

    naver_account = user_json.get("response", {})
    naver_id = naver_account.get("id")
    email = naver_account.get("email", f"naver_{naver_id}@naver.com")
    nickname = naver_account.get("nickname", f"naver_user_{naver_id}")
    profile_image = naver_account.get("profile_image", "")

    # 3. 사용자 생성 또는 가져오기
    user, created = User.objects.get_or_create(
        social_provider="naver",
        social_id=str(naver_id),
        defaults={
            "username": f"naver_{naver_id}",
            "email": email,
            "nickname": nickname,
            "profile_image": profile_image,
        },
    )

    # 4. JWT 토큰 발급
    tokens = get_tokens_for_user(user)

    return Response(
        {
            "message": "네이버 로그인 성공",
            "tokens": tokens,
            "user": UserSerializer(user).data,
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def google_login(request):
    """구글 로그인 페이지로 리다이렉트"""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=openid%20profile%20email"
    )
    return redirect(google_auth_url)


@api_view(["GET"])
@permission_classes([AllowAny])
def google_callback(request):
    """구글 로그인 콜백"""
    code = request.GET.get("code")

    # 1. 액세스 토큰 받기
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "grant_type": "authorization_code",
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
        "code": code,
    }

    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()
    access_token = token_json.get("access_token")

    # 2. 사용자 정보 받기
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(user_info_url, headers=headers)
    user_json = user_response.json()

    google_id = user_json.get("id")
    email = user_json.get("email", f"google_{google_id}@gmail.com")
    name = user_json.get("name", f"google_user_{google_id}")
    picture = user_json.get("picture", "")

    # 3. 사용자 생성 또는 가져오기
    user, created = User.objects.get_or_create(
        social_provider="google",
        social_id=str(google_id),
        defaults={
            "username": f"google_{google_id}",
            "email": email,
            "nickname": name,
            "profile_image": picture,
        },
    )

    # 4. JWT 토큰 발급
    tokens = get_tokens_for_user(user)

    return Response(
        {
            "message": "구글 로그인 성공",
            "tokens": tokens,
            "user": UserSerializer(user).data,
        }
    )


# ========================================
# 응원 팀 관련 Views
# ========================================


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_favorite_teams(request):
    """내 응원 팀 목록"""
    user = request.user
    teams = user.favorite_teams.all()
    serializer = FavoriteTeamSerializer(teams, many=True)
    return Response({"count": teams.count(), "max_count": 3, "teams": serializer.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_favorite_team(request):
    """응원 팀 추가"""
    team_id = request.data.get("team_id")

    if not team_id:
        return Response(
            {"error": "team_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        team = Team.objects.get(team_id=team_id)
    except Team.DoesNotExist:
        return Response(
            {"error": "존재하지 않는 팀입니다."}, status=status.HTTP_404_NOT_FOUND
        )

    user = request.user

    # 이미 응원 팀인지 확인
    if user.favorite_teams.filter(team_id=team_id).exists():
        return Response(
            {"error": "이미 응원 팀으로 등록되어 있습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 최대 3개 제한 확인
    if user.favorite_teams.count() >= 3:
        return Response(
            {"error": "응원 팀은 최대 3개까지만 선택할 수 있습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.favorite_teams.add(team)

    return Response(
        {
            "message": f"{team.team_name}을(를) 응원 팀으로 추가했습니다.",
            "team": FavoriteTeamSerializer(team).data,
            "current_count": user.favorite_teams.count(),
        }
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_favorite_team(request, team_id):
    """응원 팀 제거"""
    try:
        team = Team.objects.get(team_id=team_id)
    except Team.DoesNotExist:
        return Response(
            {"error": "존재하지 않는 팀입니다."}, status=status.HTTP_404_NOT_FOUND
        )

    user = request.user

    # 응원 팀인지 확인
    if not user.favorite_teams.filter(team_id=team_id).exists():
        return Response(
            {"error": "응원 팀이 아닙니다."}, status=status.HTTP_400_BAD_REQUEST
        )

    user.favorite_teams.remove(team)

    return Response(
        {
            "message": f"{team.team_name}을(를) 응원 팀에서 제거했습니다.",
            "current_count": user.favorite_teams.count(),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def all_favorite_matches(request):
    """내 모든 응원 팀의 경기 일정 (예정+지난 모두)"""
    user = request.user
    favorite_teams = user.favorite_teams.all()

    if not favorite_teams.exists():
        return Response(
            {
                "message": "응원 팀이 없습니다.",
                "teams": [],
                "upcoming_matches": [],
                "past_matches": [],
            }
        )

    from django.db.models import Q
    from django.utils import timezone

    # 모든 응원 팀의 경기 조회
    team_ids = [team.team_id for team in favorite_teams]

    q_objects = Q()
    for team_id in team_ids:
        q_objects |= Q(home_team_id=team_id) | Q(away_team_id=team_id)

    now = timezone.now()

    # 예정된 경기 (날짜순)
    upcoming_matches = Match.objects.filter(q_objects, match_date__gte=now).order_by(
        "match_date"
    )[:20]

    # 지난 경기 (최신순)
    past_matches = Match.objects.filter(q_objects, match_date__lt=now).order_by(
        "-match_date"
    )[:20]

    from matches.serializers import MatchListSerializer

    return Response(
        {
            "teams": FavoriteTeamSerializer(favorite_teams, many=True).data,
            "upcoming_count": upcoming_matches.count(),
            "past_count": past_matches.count(),
            "upcoming_matches": MatchListSerializer(upcoming_matches, many=True).data,
            "past_matches": MatchListSerializer(past_matches, many=True).data,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def favorite_team_matches(request, team_id):
    """특정 응원 팀의 경기 일정"""
    user = request.user

    # 응원 팀인지 확인
    if not user.favorite_teams.filter(team_id=team_id).exists():
        return Response(
            {"error": "응원 팀이 아닙니다."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        team = Team.objects.get(team_id=team_id)
    except Team.DoesNotExist:
        return Response(
            {"error": "존재하지 않는 팀입니다."}, status=status.HTTP_404_NOT_FOUND
        )

    from django.db.models import Q

    # 해당 팀의 경기 조회
    matches = Match.objects.filter(
        Q(home_team_id=team_id) | Q(away_team_id=team_id)
    ).order_by("-match_date")[:20]

    from matches.serializers import MatchListSerializer

    serializer = MatchListSerializer(matches, many=True)

    return Response(
        {
            "team": FavoriteTeamSerializer(team).data,
            "matches_count": matches.count(),
            "matches": serializer.data,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def upcoming_favorite_matches(request):
    """내 응원 팀의 예정된 경기"""
    user = request.user
    favorite_teams = user.favorite_teams.all()

    if not favorite_teams.exists():
        return Response({"message": "응원 팀이 없습니다.", "teams": [], "matches": []})

    from django.db.models import Q
    from django.utils import timezone

    team_ids = [team.team_id for team in favorite_teams]

    q_objects = Q()
    for team_id in team_ids:
        q_objects |= Q(home_team_id=team_id) | Q(away_team_id=team_id)

    now = timezone.now()

    # 예정된 경기 (가까운 미래부터 - 오름차순)
    matches = Match.objects.filter(q_objects, match_date__gte=now).order_by(
        "match_date"
    )[:20]

    from matches.serializers import MatchListSerializer

    return Response(
        {
            "teams": FavoriteTeamSerializer(favorite_teams, many=True).data,
            "count": matches.count(),
            "matches": MatchListSerializer(matches, many=True).data,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def past_favorite_matches(request):
    """내 응원 팀의 지난 경기"""
    user = request.user
    favorite_teams = user.favorite_teams.all()

    if not favorite_teams.exists():
        return Response({"message": "응원 팀이 없습니다.", "teams": [], "matches": []})

    from django.db.models import Q
    from django.utils import timezone

    team_ids = [team.team_id for team in favorite_teams]

    q_objects = Q()
    for team_id in team_ids:
        q_objects |= Q(home_team_id=team_id) | Q(away_team_id=team_id)

    now = timezone.now()

    # 지난 경기 (최근부터 - 내림차순)
    matches = Match.objects.filter(q_objects, match_date__lt=now).order_by(
        "-match_date"
    )[:20]

    from matches.serializers import MatchListSerializer

    return Response(
        {
            "teams": FavoriteTeamSerializer(favorite_teams, many=True).data,
            "count": matches.count(),
            "matches": MatchListSerializer(matches, many=True).data,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def main_dashboard(request):
    """메인 대시보드 - 응원 팀별 통합 정보"""
    user = request.user
    favorite_teams = user.favorite_teams.all()

    # 응원 팀이 없는 경우
    if not favorite_teams.exists():
        return Response({"favorite_teams": [], "latest_news": [], "ai_analysis": None})

    dashboard_data = []

    for team in favorite_teams:
        team_data = get_team_dashboard_data(team)
        dashboard_data.append(team_data)

    response_data = {
        "favorite_teams": dashboard_data,
        "latest_news": [],
        "ai_analysis": None,
    }

    return Response(response_data)


def get_team_dashboard_data(team):
    """팀별 대시보드 데이터 생성"""
    from django.db.models import Q
    from django.utils import timezone

    team_id = team.team_id
    team_name = team.team_name

    # 1. 순위 정보
    standing_data = None
    try:
        standing = TeamStanding.objects.get(team_name=team_name)
        win_rate = (
            (standing.wins / standing.matches_played * 100)
            if standing.matches_played > 0
            else 0
        )

        standing_data = {
            "rank": standing.rank,
            "points": standing.points,
            "wins": standing.wins,
            "draws": standing.draws,
            "losses": standing.losses,
            "win_rate": round(win_rate, 1),
            "matches_played": standing.matches_played,
            "goals_for": standing.goals_for,
            "goals_against": standing.goals_against,
            "goal_difference": standing.goal_difference,
        }
    except TeamStanding.DoesNotExist:
        pass

    # 2. 다음 경기
    next_match_data = None
    now = timezone.now()

    next_match = (
        Match.objects.filter(
            Q(home_team_id=team_id) | Q(away_team_id=team_id),
            match_date__gte=now,
            status="scheduled",
        )
        .order_by("match_date")
        .first()
    )

    if next_match:
        is_home = next_match.home_team_id == team_id
        opponent_name = (
            next_match.away_team_name if is_home else next_match.home_team_name
        )
        opponent_logo = (
            next_match.away_team_logo if is_home else next_match.home_team_logo
        )

        next_match_data = {
            "match_id": next_match.match_id,
            "match_date": next_match.match_date,
            "opponent_name": opponent_name,
            "opponent_logo": opponent_logo,
            "is_home": is_home,
            "venue": next_match.venue,
        }

    # 3. 최근 5경기 폼
    recent_form_data = None

    recent_matches = Match.objects.filter(
        Q(home_team_id=team_id) | Q(away_team_id=team_id), status="finished"
    ).order_by("-match_date")[:5]

    if recent_matches:
        form_list = []
        form_korean_list = []
        matches_data = []

        for match in reversed(list(recent_matches)):  # 오래된 것부터
            is_home = match.home_team_id == team_id
            opponent = match.away_team_name if is_home else match.home_team_name
            my_score = match.home_score if is_home else match.away_score
            opp_score = match.away_score if is_home else match.home_score

            # 승무패 판정
            if my_score > opp_score:
                result = "W"
                result_korean = "승"
            elif my_score < opp_score:
                result = "L"
                result_korean = "패"
            else:
                result = "D"
                result_korean = "무"

            form_list.append(result)
            form_korean_list.append(result_korean)

            matches_data.append(
                {
                    "match_date": match.match_date,
                    "opponent": opponent,
                    "result": result,
                    "score": f"{my_score}-{opp_score}",
                    "is_home": is_home,
                }
            )

        recent_form_data = {
            "form": "".join(form_list),
            "form_korean": "-".join(form_korean_list),
            "last_5_matches": matches_data,
        }

    # 팀 로고 가져오기 (경기 데이터에서)
    team_logo = None
    any_match = Match.objects.filter(
        Q(home_team_id=team_id) | Q(away_team_id=team_id)
    ).first()

    if any_match:
        team_logo = (
            any_match.home_team_logo
            if any_match.home_team_id == team_id
            else any_match.away_team_logo
        )

    return {
        "team_id": team_id,
        "team_name": team_name,
        "team_logo": team_logo,
        "standing": standing_data,
        "next_match": next_match_data,
        "recent_form": recent_form_data,
    }
