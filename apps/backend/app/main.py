"""Main entrypoint for the Nova AI FastAPI backend service.

Initializes the application, configures global structured logging, registers
middlewares, routes, custom exception mappings, and handles lifecycle events.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError
import structlog

from app.api.router import router as api_router
from app.core.config import settings
from app.core.constants import API_VERSION, PROJECT_NAME
from app.core.dependency_container import container
from app.core.exceptions import (
    ApplicationException,
    application_exception_handler,
    global_exception_handler,
    sqlalchemy_exception_handler,
)
from app.core.logging import configure_logging
from app.core.middleware import register_middleware

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
    # Initialize global AI Gateway container services
    from app.core.dependency_container import (
        register_ai_gateway_dependencies,
        register_workflow_dependencies,
        register_runtime_dependencies,
        resolve,
    )

    register_ai_gateway_dependencies()
    register_workflow_dependencies()
    register_runtime_dependencies()

    # Boot the Runtime Kernel
    from app.runtime.kernel import RuntimeKernel
    kernel = resolve(RuntimeKernel)
    await kernel.boot()

    yield
    logger.info("server_shutdown_initiated")

    # Gracefully stop the Runtime Kernel
    await kernel.shutdown()

    # Clean up container resource allocations on shutdown
    container.clear()


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
from app.identity.services.exceptions import (
    SecurityException,
    ExpiredTokenError,
    InvalidTokenError,
    InvalidCredentialsError,
    TokenReuseDetectedError,
)
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi import Request

async def security_exception_handler(request: Request, exc: SecurityException) -> JSONResponse:
    if isinstance(exc, ExpiredTokenError):
        code = status.HTTP_401_UNAUTHORIZED
        msg = "Token has expired."
    elif isinstance(exc, InvalidTokenError):
        code = status.HTTP_401_UNAUTHORIZED
        msg = "Invalid token."
    elif isinstance(exc, InvalidCredentialsError):
        if "already registered" in str(exc):
            code = status.HTTP_409_CONFLICT
        else:
            code = status.HTTP_401_UNAUTHORIZED
        msg = str(exc)
    elif isinstance(exc, TokenReuseDetectedError):
        code = status.HTTP_403_FORBIDDEN
        msg = str(exc)
    else:
        code = status.HTTP_400_BAD_REQUEST
        msg = str(exc)

    return JSONResponse(
        status_code=code,
        content={
            "error": exc.__class__.__name__,
            "message": msg,
        }
    )

app.add_exception_handler(SecurityException, security_exception_handler)

from app.conversation.domain.exceptions import (
    ConversationException,
    ConversationNotFoundError,
    ConversationAccessDeniedError,
    ConversationArchivedError,
    ConversationValidationError,
)

async def conversation_exception_handler(request: Request, exc: ConversationException) -> JSONResponse:
    if isinstance(exc, ConversationNotFoundError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ConversationAccessDeniedError):
        code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, (ConversationValidationError, ConversationArchivedError)):
        code = status.HTTP_400_BAD_REQUEST
    else:
        code = status.HTTP_400_BAD_REQUEST

    return JSONResponse(
        status_code=code,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
        }
    )

from app.dashboard.exceptions import (
    DashboardException,
    DashboardNotFoundError,
    NotificationNotFoundError,
    MetricNotFoundError,
    HealthRecordNotFoundError,
    EventNotFoundError,
    ConfigurationNotFoundError,
)

async def dashboard_exception_handler(request: Request, exc: DashboardException) -> JSONResponse:
    if isinstance(
        exc,
        (
            DashboardNotFoundError,
            NotificationNotFoundError,
            MetricNotFoundError,
            HealthRecordNotFoundError,
            EventNotFoundError,
            ConfigurationNotFoundError,
        ),
    ):
        code = status.HTTP_404_NOT_FOUND
    else:
        code = status.HTTP_400_BAD_REQUEST

    return JSONResponse(
        status_code=code,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
        },
    )

app.add_exception_handler(DashboardException, dashboard_exception_handler)
app.add_exception_handler(ConversationException, conversation_exception_handler)
app.add_exception_handler(ApplicationException, application_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Register all request pipelines, CORS configurations, security, and gzip filters
register_middleware(app)

# Register central routers (System status, API v1, Dashboard, etc.)
app.include_router(api_router)

from app.dashboard.routes import router as dashboard_router
from app.websocket.router import router as gateway_ws_router

app.include_router(dashboard_router)
app.include_router(gateway_ws_router)


@app.get("/", tags=["system"])
async def root() -> dict:
    """Root metadata endpoint returning basic application summary."""
    return {
        "project": PROJECT_NAME,
        "api_version": API_VERSION,
        "app_version": settings.VERSION,
        "status": "online",
    }
