"""Memory Hardware Monitor Module.

Collects real-time RAM virtual memory usage, available bytes, percentage,
and swap space metrics using psutil.
"""

from typing import Any, Dict
import psutil
import structlog

logger = structlog.get_logger(__name__)


def get_virtual_memory() -> Dict[str, Any]:
    """Returns detailed virtual memory telemetry."""
    try:
        vm = psutil.virtual_memory()
        return {
            "total": vm.total,
            "available": vm.available,
            "used": vm.used,
            "free": vm.free,
            "percent": float(vm.percent),
            "active": getattr(vm, "active", vm.used),
            "inactive": getattr(vm, "inactive", vm.free),
            "buffers": getattr(vm, "buffers", 0),
            "cached": getattr(vm, "cached", 0),
            "shared": getattr(vm, "shared", 0),
        }
    except Exception as exc:
        logger.warning("failed_to_get_virtual_memory", error=str(exc))
        return {
            "total": 0,
            "available": 0,
            "used": 0,
            "free": 0,
            "percent": 0.0,
            "active": 0,
            "inactive": 0,
            "buffers": 0,
            "cached": 0,
            "shared": 0,
        }


def get_memory_usage() -> Dict[str, Any]:
    """Returns memory usage summary (total, used, free, percent)."""
    vm = get_virtual_memory()
    return {
        "total": vm["total"],
        "used": vm["used"],
        "free": vm["free"],
        "percent": vm["percent"],
    }


def get_swap_usage() -> Dict[str, Any]:
    """Returns swap space usage metrics."""
    try:
        swap = psutil.swap_memory()
        return {
            "total": swap.total,
            "used": swap.used,
            "free": swap.free,
            "percent": float(swap.percent),
            "sin": swap.sin,
            "sout": swap.sout,
        }
    except Exception as exc:
        logger.warning("failed_to_get_swap_usage", error=str(exc))
        return {"total": 0, "used": 0, "free": 0, "percent": 0.0, "sin": 0, "sout": 0}


def get_memory_percent() -> float:
    """Returns overall RAM utilization percentage."""
    return float(get_virtual_memory()["percent"])


class MemoryMonitor:
    """Class wrapper for RAM and Swap telemetry hardware metrics."""

    def __init__(self) -> None:
        logger.info("memory_monitor_initialized")

    def get_virtual_memory(self) -> Dict[str, Any]:
        return get_virtual_memory()

    def get_memory_usage(self) -> Dict[str, Any]:
        return get_memory_usage()

    def get_swap_usage(self) -> Dict[str, Any]:
        return get_swap_usage()

    def get_memory_percent(self) -> float:
        return get_memory_percent()

    def get_metrics(self) -> Dict[str, Any]:
        """Collects complete memory metrics dictionary."""
        vm = get_virtual_memory()
        swap = get_swap_usage()
        return {
            "total": vm["total"],
            "used": vm["used"],
            "free": vm["free"],
            "available": vm["available"],
            "percent": vm["percent"],
            "swap_total": swap["total"],
            "swap_used": swap["used"],
            "swap_percent": swap["percent"],
        }
