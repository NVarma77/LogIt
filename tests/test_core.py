import json
import logging

import pytest
from django.db import connection
from django.test import Client
from structlog.stdlib import ProcessorFormatter

pytestmark = pytest.mark.django_db


def test_pg_trgm_installed() -> None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm'")
        assert cursor.fetchone() is not None


def test_response_gets_new_request_id(client: Client) -> None:
    response = client.get("/")
    assert len(response["X-Request-ID"]) == 32


def test_safe_incoming_request_id_is_reused(client: Client) -> None:
    response = client.get("/", headers={"X-Request-ID": "lb-abc.123"})
    assert response["X-Request-ID"] == "lb-abc.123"


def test_unsafe_incoming_request_id_is_replaced(client: Client) -> None:
    response = client.get("/", headers={"X-Request-ID": "bad\nvalue"})
    assert response["X-Request-ID"] != "bad\nvalue"


def test_logs_are_json_with_request_id(client: Client, caplog: pytest.LogCaptureFixture) -> None:
    client.get("/missing", headers={"X-Request-ID": "trace-me"})
    # Render what the request logged with the app's own JSON formatter.
    formatter = next(
        h.formatter
        for h in logging.getLogger().handlers
        if isinstance(h.formatter, ProcessorFormatter)
    )
    lines = [json.loads(formatter.format(record)) for record in caplog.records]
    # Both our request line and Django's own "Not Found" warning carry the ID.
    assert {"request", "Not Found: /missing"} <= {
        line["event"] for line in lines if line.get("request_id") == "trace-me"
    }
