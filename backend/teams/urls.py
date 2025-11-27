from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, StaffViewSet

router = DefaultRouter()
router.register(r"teams", TeamViewSet, basename="team")
router.register(r"staff", StaffViewSet, basename="staff")

urlpatterns = router.urls
