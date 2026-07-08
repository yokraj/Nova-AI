"""Version and build metadata details for Nova AI.

Centralizes versioning variables, application name, package definitions,
and build information to prevent duplication across the codebase.
"""

from typing import Any, Dict, Final

# Application Meta
APP_NAME: Final[str] = "Nova AI"
PACKAGE_NAME: Final[str] = "backend"
VERSION: Final[str] = "0.1.0"
API_VERSION: Final[str] = "v1"
AUTHOR: Final[str] = "Yokraj"

# Build and environment metadata
BUILD_METADATA: Final[Dict[str, Any]] = {
    "environment": "production",
    "build_number": "1",
    "git_commit": "unknown",
}
