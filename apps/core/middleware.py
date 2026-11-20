import re
import uuid
from collections.abc import Callable

import structlog
from django.http import HttpRequest, HttpResponse

logger = structlog.get_logger(__name__)

# Reuse an incoming ID only if it's short and plain, so clients can't inject junk into logs.
VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


class RequestIDMiddleware:
    """Give each request an ID, add it to every log line, and return it in X-Request-ID."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        incoming = request.headers.get("X-Request-ID", "")
        request_id = incoming if VALID_REQUEST_ID.match(incoming) else uuid.uuid4().hex

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = self.get_response(request)
        response["X-Request-ID"] = request_id
        logger.info(
            "request", method=request.method, path=request.path, status=response.status_code
        )
        return response
