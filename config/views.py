# File: config/views.py

from django.conf import settings
from django.shortcuts import redirect
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.helpers import complete_social_login
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.FRONTEND_URL + "/auth/google/callback"  # This needs to match your Google OAuth redirect URI
    client_class = OAuth2Client

def google_login_redirect(request):
    """Handle the redirect from Google OAuth callback"""
    try:
        # Redirect to frontend dashboard
        frontend_url = settings.FRONTEND_URL + "/auth/success"
        return redirect(frontend_url)
    except Exception as e:
        logger.error(f"Error in google_login_redirect: {str(e)}")
        # Redirect to signin with error
        return redirect(settings.FRONTEND_URL + "/signin?error=authentication_failed")

@csrf_exempt
def CustomGoogleCallbackView(request):
    """
    Custom callback view to handle profile_complete field error
    and improve error handling for the Google OAuth callback
    """
    try:
        # This view is meant to handle the OAuth callback from Google
        # and create/authenticate the user
        adapter = GoogleOAuth2Adapter(request)
        app = adapter.get_provider().get_app(request)
        token = adapter.parse_token({})
        token.app = app
        login = adapter.complete_login(request, app, token)
        
        # Set profile_complete to True for new users
        if not login.user.pk:  # New user being created
            login.user.profile_complete = True
            
        # Complete the social login process
        return complete_social_login(request, login)
    except Exception as e:
        logger.error(f"Error in CustomGoogleCallbackView: {str(e)}")
        # Redirect to frontend with error
        return redirect(settings.FRONTEND_URL + "/signin?error=authentication_failed")