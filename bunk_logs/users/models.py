from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.db.models import EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for Bunk Logs.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    first_name = CharField(_("First Name of User"), blank=True, max_length=255)  # type: ignore[assignment]
    last_name = CharField(_("Last Name of User"), blank=True, max_length=255)  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    ADMIN = "Admin"
    CAMPER_CARE = "Camper Care"
    UNIT_HEAD = "Unit Head"
    COUNSELOR = "Counselor"

    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (CAMPER_CARE, "Camper Care"),
        (UNIT_HEAD, "Unit Head"),
        (COUNSELOR, "Counselor"),
    ]

    role = models.CharField(
        max_length=255,
        choices=ROLE_CHOICES,
        blank=True,
        default="",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    class Meta:
        app_label = "users"

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})
