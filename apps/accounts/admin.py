from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import User


@admin.register(User)
class LogItUserAdmin(UserAdmin):  # type: ignore[type-arg]
    # Email is required, so the "add user" form must ask for it.
    add_fieldsets = ((None, {"fields": ("username", "email", "password1", "password2")}),)
