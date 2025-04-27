from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserDetailsView, basename='user')
# Add other viewsets to the router
router.register(r'bunks', views.BunkViewSet, basename='bunk')
router.register(r'units', views.UnitViewSet, basename='unit')
router.register(r'campers', views.CamperViewSet, basename='camper')
router.register(r'camper-bunk-assignments', views.CamperBunkAssignmentViewSet, basename='camper-bunk-assignment')
router.register(r'bunklogs', views.BunkLogViewSet, basename='bunklog')

urlpatterns = [
    path('', include(router.urls)),
    
    # Add dedicated endpoint for email-based user retrieval
    path('users/email/<str:email>/', views.get_user_by_email, name='user-by-email'),
    
    # Debug endpoints
    path('debug/user-bunks/', views.debug_user_bunks, name='debug-user-bunks'),
    path('debug/fix-social-apps/', views.fix_social_apps, name='fix-social-apps'),
    path('debug/auth/', views.auth_debug_view, name='auth-debug'),
    
    # Add a URL pattern for the BunkLogsInfoByDateViewSet
    path('bunklogs/<str:bunk_id>/logs/<str:date>/', views.BunkLogsInfoByDateViewSet.as_view(), name='bunklog-by-date'),
    
    # URL for camper bunk logs
    path('campers/<str:camper_id>/logs/', views.CamperBunkLogViewSet.as_view(), name='camper-bunklogs'),
]
