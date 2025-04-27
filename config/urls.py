from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include, re_path
from django.views import defaults as default_views
from django.views.generic import TemplateView, RedirectView
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.renderers import JSONRenderer

from rest_framework_simplejwt.views import TokenRefreshView
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import UserDetailsView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

# Import GoogleCallbackView from your app - This will now use the updated version
from bunk_logs.users.views import GoogleCallbackView, CustomEmailVerificationSentView

# Social Signin
from rest_framework.authtoken.views import obtain_auth_token
from .views import GoogleLogin, google_login_redirect
# Remove the CustomGoogleCallbackView import since we're not using it anymore
from .auth_api import get_csrf_token, get_auth_status
from django.contrib.auth import get_user_model
from .serializers import CustomUserDetailsSerializer

User = get_user_model()

# Custom User Details View to ensure JSON response
class JSONUserDetailsView(UserDetailsView):
    serializer_class = CustomUserDetailsSerializer
    renderer_classes = [JSONRenderer]
    
    def get_serializer_class(self):
        return self.serializer_class
    
    def get_object(self):
        return self.request.user
    
    def get_response(self):
        serializer = self.get_serializer(instance=self.get_object())
        user = self.request.user
        data = serializer.data
        
        # If you want to add groups as a special case (since it's a many-to-many field)
        data['groups'] = [group.name for group in user.groups.all()]
        
        # Add any other custom fields not included in the serializer
        # data['custom_field'] = user.custom_field
        
        return Response(data)

@csrf_exempt
def complete_social_login(request):
    """
    View that completes social login and redirects to frontend with token
    """
    if request.user.is_authenticated:
        # Generate JWT tokens
        refresh = RefreshToken.for_user(request.user)
        
        # Redirect to frontend with token in URL params
        frontend_url = settings.LOGIN_REDIRECT_URL
        if '?' in frontend_url:
            redirect_url = f"{frontend_url}&token={str(refresh.access_token)}"
        else:
            redirect_url = f"{frontend_url}?token={str(refresh.access_token)}"
        
        return HttpResponseRedirect(redirect_url)
    else:
        # Redirect to login page if not authenticated
        return HttpResponseRedirect(settings.ACCOUNT_LOGOUT_REDIRECT_URL)

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    # Temporarily comment out this path until the user_detail_view is properly defined
    # path("users/", include("bunk_logs.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Auth API endpoints
    path('api/v1/csrf-token/', get_csrf_token),
    path('api/v1/auth-status/', get_auth_status),

    # JWT token endpoints
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # dj-rest-auth endpoints
    path("api/v1/auth/", include("dj_rest_auth.urls")),
    # Override the user details endpoint to ensure JSON response
    path("api/v1/auth/user/", JSONUserDetailsView.as_view(), name="rest_user_details"),
    path("api/v1/auth/registration/", include("dj_rest_auth.registration.urls")),

    # Social auth endpoints
    path('api/v1/auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('api/v1/auth/google/callback/', google_login_redirect, name='google_login_callback'),
    
    # Complete social login view
    path('auth/complete/', complete_social_login, name='complete_social_login'),

    # This special path will handle the redirect after Google authentication
    # and redirect to your frontend
    re_path(r'^auth/callback/?$', 
        TemplateView.as_view(template_name="socialaccount/callback.html"), 
        name="google_callback_redirect"),


    # Override the email verification sent view
    path(
        "api/v1/auth/registration/account-email-verification-sent/",  # Added trailing slash
        CustomEmailVerificationSentView.as_view(),
        name="account_email_verification_sent",
    ),
    # Your stuff: custom urls includes go here
    path("api/v1/", include("bunk_logs.api.urls")),
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),

    path('api/v1/auth/token/', obtain_auth_token, name='api_token_auth'),
    
    path('accounts/google/login/callback/', 
         RedirectView.as_view(url=settings.LOGIN_REDIRECT_URL),
         name='google_callback_redirect'),
         
    path('accounts/social/connections/', 
     TemplateView.as_view(template_name='socialaccount/connections.html'),
     name='socialaccount_connections'),

    # Use GoogleCallbackView instead of CustomGoogleCallbackView to handle the Google OAuth callback
    path('api/v1/auth/social/google/callback/', csrf_exempt(GoogleCallbackView.as_view()), name='google_callback'),
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
