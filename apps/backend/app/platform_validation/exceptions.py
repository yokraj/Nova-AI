"""Platform Validation Exception Hierarchy Module.

Defines domain-specific exception types for Nova AI Enterprise Platform Validation Suite.
"""

from typing import Any, Dict, Optional


class ValidationPlatformError(Exception):
    """Base exception class for all Platform Validation errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class BenchmarkFailedError(ValidationPlatformError):
    """Raised when performance benchmark fails to meet target SLA."""
    pass


class StressTestFailedError(ValidationPlatformError):
    """Raised when load or stress test fails under concurrency."""
    pass


class SecurityAuditFailedError(ValidationPlatformError):
    """Raised when security audit detects RBAC or isolation vulnerabilities."""
    pass


class BackupFailedError(ValidationPlatformError):
    """Raised when automated backup snapshot or integrity verification fails."""
    pass


class RecoveryFailedError(ValidationPlatformError):
    """Raised when disaster recovery state restoration fails."""
    pass


class ProductionReadinessError(ValidationPlatformError):
    """Raised when production release readiness checks fail."""
    pass
