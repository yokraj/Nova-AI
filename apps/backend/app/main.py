"""Main entrypoint for the Nova AI FastAPI backend service.

Initializes the application, configures middlewares (CORS, Request Logging),
registers global exception handlers, sets up the lifespan logger, and exposes
the system utility endpoints.
"""

from contextlib import asynccontextmanager
import time
from typing import Any, AsyncGenerator
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
import structlog

from app.core.config import settings
from app.core.constants import API_VERSION, HEALTH_STATUS_OK, PROJECT_NAME
from app.core.exceptions import (
    ApplicationException,
    application_exception_handler,
    global_exception_handler,
    sqlalchemy_exception_handler,
)
from app.core.logging import (
    bind_request_context,
    clear_request_context,
    configure_logging,
)

# Configure structured logging before application boot
configure_logging(log_level=settings.LOG_LEVEL, debug=settings.DEBUG)
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and shutdown lifecycle events."""
    logger.info(
        "server_startup_initiated",
        project=PROJECT_NAME,
        version=settings.VERSION,
        debug_mode=settings.DEBUG,
        host=settings.HOST,
        port=settings.PORT,
    )
    yield
    logger.info("server_shutdown_initiated")


# OpenAPI documentation tag definitions
tags_metadata = [
    {
        "name": "system",
        "description": "System status, health checks, and lifecycle parameters.",
    }
]

app = FastAPI(
    title=PROJECT_NAME,
    version=settings.VERSION,
    description="The Universal AI Operating Layer REST API Service",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"/api/{API_VERSION}/openapi.json",
    openapi_tags=tags_metadata,
)

# Register custom and global fallback exception handlers
app.add_exception_handler(ApplicationException, application_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Configure CORS policies
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next: Any) -> Any:
    """HTTP Middleware logging incoming requests and responses with trace context."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    correlation_id = request.headers.get("X-Correlation-ID", request_id)

    # Bind request trace IDs to structlog contextvars
    bind_request_context(
        request_id=request_id, correlation_id=correlation_id, user_id=None
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
        execution_time_ms = (time.perf_counter() - start_time) * 1000

        # Inject tracing headers into the response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Correlation-ID"] = correlation_id

        logger.info(
            "http_response_sent",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            execution_time_ms=round(execution_time_ms, 2),
        )
        return response
    except Exception as e:
        execution_time_ms = (time.perf_counter() - start_time) * 1000
        logger.error(
            "http_request_failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
            execution_time_ms=round(execution_time_ms, 2),
        )
        raise
    finally:
        # Clear contextvars to prevent pollution of log contexts across request loops
        clear_request_context()


@app.get("/", tags=["system"])
async def root() -> dict:
    """Root metadata endpoint returning basic application summary."""
    return {
        "project": PROJECT_NAME,
        "api_version": API_VERSION,
        "app_version": settings.VERSION,
        "status": "online",
    }


@app.get("/health", tags=["system"])
async def health_check() -> dict:
    """Basic health check endpoint validating server availability."""
    return {
        "status": HEALTH_STATUS_OK,
        "version": settings.VERSION,
    }
