"""Custom and library middleware setups for the Nova AI application.

Implements request tracing, timing headers, custom security settings,
and configures standard GZip and Trusted Host filters.
"""

import time
from typing import Any, Callable, Coroutine
import uuid
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from app.core.config import settings
from app.core.logging import bind_request_context, clear_request_context

logger = structlog.get_logger(__name__)


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """Middleware for injecting Request-ID and Correlation-ID trace headers."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Coroutine[Any, Any, Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        correlation_id = request.headers.get("X-Correlation-ID", request_id)

        # Bind tracing parameters to the structured logging context
        bind_request_context(
            request_id=request_id, correlation_id=correlation_id
        )

        logger.info(
            "http_request_received",
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else None,
        )

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Attach request IDs back to the response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id

            logger.info(
                "http_request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )
            return response
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "http_request_failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_ms=round(duration_ms, 2),
            )
            raise
        finally:
            # Prevent trace leaks across thread spans
            clear_request_context()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforces standard HTTP security protection headers on all responses."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Coroutine[Any, Any, Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; frame-ancestors 'none';"
        )
        response.headers["Referrer-Policy"] = (
            "strict-origin-when-cross-origin"
        )
        return response


def register_middleware(app: FastAPI) -> None:
    """Registers all middleware layers onto the FastAPI application.

    Args:
        app: The FastAPI application instance to register middleware on.
    """
    # 1. Custom Request Tracing & Timing
    app.add_middleware(RequestTracingMiddleware)

    # 2. CORS Policy Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 3. HTTP Security Headers
    app.add_middleware(SecurityHeadersMiddleware)

    # 4. GZip Response Compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 5. Trusted Host validation (active in production mode)
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=[settings.HOST, "localhost", "127.0.0.1", "testserver"],
        )
