from django.contrib.auth.password_validation import validate_password

from apps.accounts.models import User


def register_user(*, username: str, email: str, password: str) -> User:
    """Create an account. Raises ValidationError if any rule fails."""
    user = User(username=username.strip(), email=User.objects.normalize_email(email))
    user.full_clean(exclude=["password"])
    validate_password(password, user=user)
    user.set_password(password)
    user.save()
    return user
