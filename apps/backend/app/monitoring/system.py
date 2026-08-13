"""System Metadata & Telemetry Monitor Module.

Collects host machine OS metadata, kernel release, hardware architecture,
boot timestamp, uptime seconds, Python runtime environment, and environment flags.
"""

from datetime import datetime, timezone
import os
import platform
import sys
import time
from typing import Any, Dict
import psutil
import structlog

logger = structlog.get_logger(__name__)


def get_os() -> str:
    """Returns Operating System name and release (e.g. Windows 11, Linux 6.1)."""
    try:
        return f"{platform.system()} {platform.release()}"
    except Exception:
        return "Unknown OS"


def get_kernel() -> str:
    """Returns OS kernel version string."""
    try:
        return platform.version()
    except Exception:
        return "Unknown Kernel"


def get_machine() -> str:
    """Returns hardware machine type (e.g. AMD64, x86_64, arm64)."""
    try:
        return platform.machine()
    except Exception:
        return "Unknown Machine"


def get_architecture() -> str:
    """Returns Python interpreter architecture (e.g. 64bit, 32bit)."""
    try:
        return platform.architecture()[0]
    except Exception:
        return "Unknown Architecture"


def get_boot_time() -> datetime:
    """Returns host machine boot time timestamp in UTC."""
    try:
        bt = psutil.boot_time()
        return datetime.fromtimestamp(bt, tz=timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def get_uptime() -> float:
    """Returns host machine uptime duration in seconds."""
    try:
        return float(time.time() - psutil.boot_time())
    except Exception:
        return 0.0


def get_python_version() -> str:
    """Returns active Python runtime version string."""
    return sys.version.split()[0]


def get_environment() -> Dict[str, str]:
    """Returns safe environment variables dictionary (sanitizing secrets)."""
    safe_env = {}
    sensitive_keys = {"KEY", "SECRET", "PASSWORD", "TOKEN", "AUTH", "CREDENTIAL"}
    for k, v in os.environ.items():
        if any(s in k.upper() for s in sensitive_keys):
            safe_env[k] = "******"
        else:
            safe_env[k] = v
    return safe_env


def get_system_information() -> Dict[str, Any]:
    """Returns comprehensive host system information dictionary."""
    return {
        "hostname": platform.node(),
        "os_name": get_os(),
        "kernel": get_kernel(),
        "machine": get_machine(),
        "architecture": get_architecture(),
        "boot_time": get_boot_time().isoformat(),
        "uptime_seconds": get_uptime(),
        "python_version": get_python_version(),
    }


class SystemMonitor:
    """Class wrapper for Host System OS and Environment metadata telemetry."""

    def __init__(self) -> None:
        logger.info("system_monitor_initialized")

    def get_os(self) -> str:
        return get_os()

    def get_kernel(self) -> str:
        return get_kernel()

    def get_machine(self) -> str:
        return get_machine()

    def get_architecture(self) -> str:
        return get_architecture()

    def get_boot_time(self) -> datetime:
        return get_boot_time()

    def get_uptime(self) -> float:
        return get_uptime()

    def get_python_version(self) -> str:
        return get_python_version()

    def get_environment(self) -> Dict[str, str]:
        return get_environment()

    def get_system_information(self) -> Dict[str, Any]:
        return get_system_information()


# Preserve legacy imports for backwards compatibility
class ResourceMonitor:
    """Legacy ResourceMonitor wrapper."""

    def __init__(self) -> None:
        pass


class SystemMonitorService:
    """Legacy SystemMonitorService wrapper."""

    def __init__(self) -> None:
        pass
