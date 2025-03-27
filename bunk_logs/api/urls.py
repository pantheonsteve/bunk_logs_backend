from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BunkViewSet
from .views import CamperBunkAssignmentViewSet
from .views import CamperViewSet
from .views import UnitViewSet

router = DefaultRouter()
router.register(r"bunks", BunkViewSet)
router.register(r"units", UnitViewSet)
router.register(r"campers", CamperViewSet)
router.register(r"bunk-assignments", CamperBunkAssignmentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
