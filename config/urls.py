from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from bunk_logs.users.views import (
    GoogleLoginView,
    GoogleCallbackView,
    CustomEmailVerificationSentView,
    get_csrf_token,
    get_auth_status,
    logout_view,
    token_refresh,
    token_authenticate,
)

urlpatterns = [
    # Admin URL
    path(settings.ADMIN_URL, admin.site.urls),
    
    # User management
    path("accounts/", include("allauth.urls")),
    
    # API Auth endpoints 
    path('auth/token/refresh/', token_refresh),
    path('auth/token/authenticate/', token_authenticate),  # New endpoint for token-based auth
    path('auth/token/verify/', token_refresh, name='token_verification'),  # Add token verification endpoint
    path('auth/csrf-token/', get_csrf_token),
    path('auth/status/', get_auth_status),
    path('auth/logout/', logout_view),
    
    # Social auth
    path('auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('auth/callback/', GoogleCallbackView.as_view(), name='google_callback'),
    
    # Custom email verification view
    path('auth/registration/account-email-verification-sent/', 
         CustomEmailVerificationSentView.as_view(), 
         name='account_email_verification_sent'),
    
    # Django Rest Auth URLs
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    
    # Auth callback page for frontend
    re_path(r'^auth/callback/?$', 
        TemplateView.as_view(template_name="socialaccount/callback.html"), 
        name="google_callback_redirect"),
    
    # Your app-specific API URLs
    path("api/v1/", include("bunk_logs.api.urls")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns