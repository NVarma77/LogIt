import uuid

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import Client

from apps.accounts.models import User
from apps.accounts.services import register_user

pytestmark = pytest.mark.django_db

PASSWORD = "correct-horse-battery-staple"


def make_user(username: str = "NeelV", email: str = "neel@example.com") -> User:
    return register_user(username=username, email=email, password=PASSWORD)


def test_register_user() -> None:
    user = make_user(email=" Neel@Example.COM ")
    assert user.username == "NeelV"
    assert user.email == "neel@example.com"
    assert user.check_password(PASSWORD)
    assert isinstance(user.pk, uuid.UUID)


def test_create_superuser_lowercases_email() -> None:
    """createsuperuser and the admin don't go through register_user."""
    user = User.objects.create_superuser("Boss", "Boss@Example.com", PASSWORD)
    assert user.email == "boss@example.com"


def test_admin_can_add_user(client: Client) -> None:
    client.force_login(User.objects.create_superuser("Boss", "boss@example.com", PASSWORD))
    response = client.post(
        "/admin/accounts/user/add/",
        {
            "username": "NewPerson",
            "email": "New@Example.com",
            "usable_password": "true",
            "password1": PASSWORD,
            "password2": PASSWORD,
        },
    )
    assert response.status_code == 302
    assert User.objects.get(username="NewPerson").email == "new@example.com"


def test_username_unique_ignoring_case() -> None:
    make_user(username="NeelV")
    with pytest.raises(ValidationError, match="That username is taken."):
        make_user(username="neelv", email="other@example.com")


def test_email_unique_ignoring_case() -> None:
    make_user(email="neel@example.com")
    with pytest.raises(ValidationError):
        make_user(username="someone", email="NEEL@example.com")


def test_database_enforces_rules_even_without_validation() -> None:
    User.objects.create(username="NeelV", email="a@example.com")
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create(username="NEELV", email="b@example.com")
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create(username="someone", email="UPPER@example.com")


@pytest.mark.parametrize("name", ["Admin", "ab", "has space", "naïve"])
def test_bad_usernames_rejected(name: str) -> None:
    with pytest.raises(ValidationError):
        make_user(username=name)


def test_weak_password_rejected() -> None:
    with pytest.raises(ValidationError):
        register_user(username="NeelV", email="neel@example.com", password="123")
