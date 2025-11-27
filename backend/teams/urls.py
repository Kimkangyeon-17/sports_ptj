from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, StaffViewSet, TeamStandingViewSet

router = DefaultRouter()
router.register(r"teams", TeamViewSet, basename="team")
router.register(r"staff", StaffViewSet, basename="staff")
router.register(r"standings", TeamStandingViewSet, basename="standing")

urlpatterns = [
    path("", include(router.urls)),
]
