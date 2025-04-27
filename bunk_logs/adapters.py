from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter for django-allauth.
    
    This can be extended to customize default behavior like email verification,
    signup process, etc.
    """
    
    def is_open_for_signup(self, request):
        """
        Determines whether a user can sign up.
        """
        return True


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter for django-allauth.
    
    This can be extended to customize social authentication behavior.
    """
    
    def is_open_for_signup(self, request, sociallogin):
        """
        Determines whether a user can sign up using social accounts.
        """
        return True