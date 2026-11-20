from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

# Usernames go in profile URLs, so keep them to plain ASCII.
username_format_validator = RegexValidator(
    regex=r"^[A-Za-z0-9_]{3,30}$",
    message="Usernames must be 3-30 characters: letters, numbers, and underscores.",
)

RESERVED_USERNAMES = {"admin", "settings", "login", "logout", "signup", "me", "api"}


def reserved_username_validator(value: str) -> None:
    if value.lower() in RESERVED_USERNAMES:
        raise ValidationError("That username is reserved.")
