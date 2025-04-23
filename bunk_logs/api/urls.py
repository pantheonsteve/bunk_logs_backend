from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BunkViewSet
from .views import CamperBunkAssignmentViewSet
from .views import CamperViewSet
from .views import UnitViewSet
from .views import BunkLogsInfoByDateViewSet
from .views import BunkLogViewSet
from .views import CamperBunkLogViewSet
from .views import debug_user_bunks

router = DefaultRouter()
router.register(r"bunks", BunkViewSet)
router.register(r"units", UnitViewSet)
router.register(r"campers", CamperViewSet)
router.register(r"bunk-assignments", CamperBunkAssignmentViewSet)
router.register(r"bunklogs", BunkLogViewSet)
# Removed the following line that was causing the conflict:
# router.register(r"camper", CamperBunkLogViewSet, basename="camper-bunklogs")

urlpatterns = [
    path("", include(router.urls)),
    path("bunklogs/<str:bunk_id>/<str:date>/", BunkLogsInfoByDateViewSet.as_view(), name="bunk-logs-info"),
    path("camper/<str:camper_id>/", CamperBunkLogViewSet.as_view(), name="camper-bunklogs"),
    path('debug/user-bunks/', debug_user_bunks, name='debug-user-bunks'),
]
