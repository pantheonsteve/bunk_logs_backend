from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
import requests


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
import json

class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://localhost:5173/auth/callback'  # Must match Google OAuth
    client_class = OAuth2Client

# Use standard APIView instead
class CustomEmailVerificationSentView(APIView):
    """
    Custom view for handling email verification sent status.
    This replaces the VerificationSentView that couldn't be imported.
    """
    def get(self, request, *args, **kwargs):
        return Response(
            {"detail": "Verification email has been sent to your email address."},
            status=status.HTTP_200_OK
        )

# Add this new view to handle the code exchange
@method_decorator(csrf_exempt, name='dispatch')
class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Extract authorization code and state from query parameters
        code = request.GET.get('code')
        
        if not code:
            return Response({"error": "No authorization code provided"}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Get the current site
            current_site = Site.objects.get_current()
            
            # Get the Google SocialApp for this site
            social_app = SocialApp.objects.get(provider='google', sites=current_site)
            
            # Exchange code for token with Google
            token_response = requests.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'code': code,
                    'client_id': social_app.client_id,
                    'client_secret': social_app.secret,
                    'redirect_uri': 'http://localhost:8000/api/v1/auth/social/google/callback/',
                    'grant_type': 'authorization_code'
                }
            )
            
            tokens = token_response.json()
            
            if 'error' in tokens:
                return Response({"error": tokens.get('error_description', tokens['error'])}, 
                              status=status.HTTP_400_BAD_REQUEST)
                
            # Use the token to get user info
            user_info_response = requests.get(
                'https://www.googleapis.com/oauth2/v3/userinfo',
                headers={'Authorization': f"Bearer {tokens['access_token']}"}
            )
            
            user_info = user_info_response.json()
            
            # For now, just redirect to the frontend with the user info
            # URL encode the JSON data to safely pass it in the URL
            import urllib.parse
            encoded_data = urllib.parse.quote(json.dumps(user_info))
            
            redirect_url = f"http://localhost:5173/auth/success?data={encoded_data}"
            return redirect(redirect_url)
            
        except SocialApp.DoesNotExist:
            return Response(
                {"error": "Google OAuth application not found in the database. Please configure it in the admin."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Site.DoesNotExist:
            return Response(
                {"error": "Site configuration is missing."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            import traceback
            print(f"Error in Google callback: {str(e)}")
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)