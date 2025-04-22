from __future__ import annotations

import typing

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialLogin
    from django.http import HttpRequest

    from bunk_logs.users.models import User


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def get_email_confirmation_url(self, request, emailconfirmation):
        """Constructs the email confirmation (activation) url.

        Note that if you have architected your system such that email
        confirmations are sent outside of the request context `request`
        can be `None` here.
        """
        url = super().get_email_confirmation_url(request, emailconfirmation)
        # Override for SPA redirect
        if settings.DEBUG:  # Use localhost URL in development
            return f"{settings.SPA_URL}/verify-email/{emailconfirmation.key}"
        return url


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        data: dict[str, typing.Any],
    ) -> User:
        """
        Populates user information from social provider info.

        See: https://docs.allauth.org/en/latest/socialaccount/advanced.html#creating-and-populating-user-instances
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Get name data from provider
        if not user.first_name or not user.last_name:
            if name := data.get("name"):
                parts = name.split()
                if len(parts) > 1:
                    user.first_name = parts[0]
                    user.last_name = " ".join(parts[1:])
                else:
                    user.first_name = name
            elif first_name := data.get("first_name"):
                user.first_name = first_name
                if last_name := data.get("last_name"):
                    user.last_name = last_name
        
        # Mark new social users as needing profile completion
        if not getattr(user, 'pk', None):
            user.profile_complete = False
            
        return user
