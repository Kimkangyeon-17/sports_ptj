from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from players.views import PlayerViewSet
from teams.views import TeamViewSet, StaffViewSet, TeamStandingViewSet

router = DefaultRouter()
router.register(r"players", PlayerViewSet, basename="player")
router.register(r"teams", TeamViewSet, basename="team")
router.register(r"staff", StaffViewSet, basename="staff")
router.register(r"standings", TeamStandingViewSet, basename="standing")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path("api/", include("matches.urls")),
    path("api/", include(router.urls)),  # 통합된 라우터
]
