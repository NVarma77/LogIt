import uuid
from typing import ClassVar

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models.functions import Lower

from apps.accounts.validators import reserved_username_validator, username_format_validator


class LogItUserManager(UserManager):  # type: ignore[type-arg]
    @classmethod
    def normalize_email(cls, email: str | None) -> str:
        # Django only lowercases the domain. Every user-creation path and Model.clean() call this.
        return (email or "").strip().lower()


class User(AbstractUser):
    # UUID so URLs don't reveal how many users exist.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[username_format_validator, reserved_username_validator],
    )
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=50, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: ClassVar[LogItUserManager] = LogItUserManager()

    class Meta:
        constraints = [
            # "NeelV" and "neelv" can't both exist.
            models.UniqueConstraint(
                Lower("username"),
                name="accounts_user_username_ci_unique",
                violation_error_message="That username is taken.",
            ),
            # Emails are stored lowercase; the database rejects anything else.
            models.CheckConstraint(
                condition=models.Q(email=Lower("email")),
                name="accounts_user_email_lowercase",
                violation_error_message="Email must be lowercase.",
            ),
        ]
