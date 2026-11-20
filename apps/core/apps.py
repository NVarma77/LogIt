from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Shared infrastructure: logging, request IDs, Postgres extensions."""

    name = "apps.core"
    label = "core"
