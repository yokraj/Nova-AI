"""Platform Validation REST API Endpoints Module.

Provides OpenAPI-compliant endpoints for benchmarking, health diagnostics, security audit,
automated backups, and production release readiness, guarded by RBAC permissions.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.identity.infrastructure.rbac import PermissionChecker
from app.platform_validation.benchmark import PlatformBenchmarker
from app.platform_validation.health_monitor import PlatformHealthMonitor
from app.platform_validation.security_audit import SecurityAuditor
from app.platform_validation.backup import BackupManager
from app.platform_validation.release_manager import ReleaseManager
from app.platform_validation.stress_testing import StressTestRunner

router = APIRouter(prefix="/api/v1/validation", tags=["Enterprise Platform Validation"])

# Permission dependencies
require_platform_read = Depends(PermissionChecker("platform:read"))
require_platform_write = Depends(PermissionChecker("platform:write"))
require_platform_admin = Depends(PermissionChecker("platform:admin"))


@router.post("/benchmark", status_code=status.HTTP_200_OK, dependencies=[require_platform_write])
async def run_benchmark() -> Any:
    """Executes full benchmark suite across all 7 Memory Platform sub-engines."""
    benchmarker = PlatformBenchmarker()
    return await benchmarker.run_full_benchmark()


@router.get("/health", status_code=status.HTTP_200_OK, dependencies=[require_platform_read])
async def get_platform_health() -> Any:
    """Executes health checks across all 7 Memory Platform sub-engines."""
    health_monitor = PlatformHealthMonitor()
    return health_monitor.run_platform_health_checks()


@router.get("/security", status_code=status.HTTP_200_OK, dependencies=[require_platform_read])
async def audit_security() -> Any:
    """Executes security audit across permissions matrix and tenant isolation."""
    auditor = SecurityAuditor()
    return auditor.audit_security()


@router.post("/backup", status_code=status.HTTP_201_CREATED, dependencies=[require_platform_write])
async def create_backup() -> Any:
    """Creates timestamped snapshot backup of Memory Platform databases and indexes."""
    backup_mgr = BackupManager()
    return backup_mgr.create_snapshot(backup_type="full")


@router.get("/release", status_code=status.HTTP_200_OK, dependencies=[require_platform_read])
async def verify_release_readiness() -> Any:
    """Verifies production release readiness and generates release documentation."""
    benchmarker = PlatformBenchmarker()
    auditor = SecurityAuditor()
    stress_runner = StressTestRunner()
    release_mgr = ReleaseManager()

    bench_res = await benchmarker.run_full_benchmark()
    sec_res = auditor.audit_security()
    stress_res = await stress_runner.run_stress_test()

    readiness = release_mgr.verify_release_readiness(bench_res, sec_res, stress_res)
    docs = release_mgr.generate_release_documentation()

    return {
        "readiness": readiness,
        "documentation": docs,
    }
