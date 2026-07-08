"""Application constants for Nova AI.

This module defines global, immutable configuration variables and constant strings
used throughout the Nova AI backend.
"""

from typing import Final
from app.core.version import API_VERSION, APP_NAME

# Health Check Statuses
HEALTH_STATUS_OK: Final[str] = "healthy"
HEALTH_STATUS_UNHEALTHY: Final[str] = "unhealthy"

# Default Preferences
DEFAULT_TIMEZONE: Final[str] = "UTC"

# Application-wide Defaults
DEFAULT_PAGE_SIZE: Final[int] = 20
MAX_PAGE_SIZE: Final[int] = 100
