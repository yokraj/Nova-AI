"""Custom application exceptions and global error handlers for Nova AI.

Defines custom subclasses of ApplicationException mapping to target status codes,
along with FastAPI handlers returning clean JSON responses.
"""

from typing import Any, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import structlog

logger = structlog.get_logger(__name__)


class ApplicationException(Exception):
    """Base exception class for all custom Nova AI errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class ConfigurationException(ApplicationException):
    """Exception raised for configuration mismatch or parsing errors."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class DatabaseException(ApplicationException):
    """Exception raised for database connectivity or query failures."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class ValidationException(ApplicationException):
    """Exception raised for request payload format validation failures."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


async def application_exception_handler(
    request: Request, exc: ApplicationException
) -> JSONResponse:
    """FastAPI error handler mapping ApplicationException and subclasses.

    Logs error structure and returns parsed JSON to client.
    """
    logger.error(
        "application_exception",
        path=request.url.path,
        error_type=exc.__class__.__name__,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """Handles SQLAlchemy errors, masking them to avoid leaking db architecture details.

    Logs full db tracebacks for internal debugging.
    """
    logger.exception(
        "database_query_failed", path=request.url.path, error=str(exc)
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "DatabaseError",
            "message": "A database operation failed. The details have been logged internally.",
        },
    )


async def global_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """FastAPI error handler mapping unhandled/unexpected system exceptions.

    Logs full traceback exception stack and returns generic 500 error map.
    """
    logger.exception(
        "unhandled_system_exception", path=request.url.path, error=str(exc)
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Please contact system support.",
        },
    )
