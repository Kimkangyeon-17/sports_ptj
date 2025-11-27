from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken
import requests
import os
from .serializers import UserSerializer, UserRegisterSerializer

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
