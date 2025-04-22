# ruff: noqa
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import TemplateView
# Social Signin
from rest_framework.authtoken.views import obtain_auth_token
from .views import GoogleLogin, google_login_redirect, CustomGoogleCallbackView
from .auth_api import get_csrf_token, get_auth_status
from bunk_logs.users.views import CustomEmailVerificationSentView

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("bunk_logs.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Auth API endpoints
    path('api/v1/csrf-token/', get_csrf_token),
    path('api/v1/auth-status/', get_auth_status),
    # Override the email verification sent view
    path(
        "api/v1/auth/registration/account-email-verification-sent",
        CustomEmailVerificationSentView.as_view(),
        name="account_email_verification_sent",
    ),
    # Your stuff: custom urls includes go here
    path("api/v1/", include("bunk_logs.api.urls")),
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),

    path('api/v1/auth/', include('dj_rest_auth.urls')),
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/v1/auth/token/', obtain_auth_token, name='api_token_auth'),
    path('api/v1/auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('api/v1/auth/google/callback/', google_login_redirect, name='google_login_callback'),
    
    # Override the default allauth Google callback to handle missing profile_complete field
    path('accounts/google/login/callback/', CustomGoogleCallbackView, name='google_callback'),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()
