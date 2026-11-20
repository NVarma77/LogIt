from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    """Enable pg_trgm for typo-tolerant topic search (similarity() and GIN trigram indexes)."""

    dependencies = []

    operations = [TrigramExtension()]
