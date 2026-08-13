"""Disk Hardware Monitor Module.

Collects real-time storage partition usage, free space, mount points,
and read/write I/O performance metrics using psutil and pathlib.
"""

import os
from pathlib import Path
from typing import Any, Dict, List
import psutil
import structlog

logger = structlog.get_logger(__name__)


def get_disk_partitions() -> List[Dict[str, Any]]:
    """Returns list of all attached storage disk partitions."""
    partitions = []
    try:
        for part in psutil.disk_partitions(all=False):
            partitions.append(
                {
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "opts": part.opts,
                }
            )
    except Exception as exc:
        logger.warning("failed_to_get_disk_partitions", error=str(exc))
    return partitions


def get_free_space(path: str = "/") -> Dict[str, Any]:
    """Returns total, used, free bytes and usage percent for specified path."""
    try:
        # Fallback to root or C: on Windows if path doesn't exist
        target_path = path if os.path.exists(path) else ("C:\\" if os.name == "nt" else "/")
        usage = psutil.disk_usage(target_path)
        return {
            "path": target_path,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": float(usage.percent),
        }
    except Exception as exc:
        logger.warning("failed_to_get_free_space", path=path, error=str(exc))
        return {"path": path, "total": 0, "used": 0, "free": 0, "percent": 0.0}


def get_disk_usage() -> Dict[str, Any]:
    """Returns root mount point disk usage summary."""
    default_root = "C:\\" if os.name == "nt" else "/"
    return get_free_space(default_root)


def get_disk_io() -> Dict[str, Any]:
    """Returns cumulative disk I/O metrics (read_bytes, write_bytes, counts)."""
    try:
        io = psutil.disk_io_counters()
        if io:
            return {
                "read_count": io.read_count,
                "write_count": io.write_count,
                "read_bytes": io.read_bytes,
                "write_bytes": io.write_bytes,
                "read_time": getattr(io, "read_time", 0),
                "write_time": getattr(io, "write_time", 0),
            }
    except Exception as exc:
        logger.warning("failed_to_get_disk_io", error=str(exc))
    return {
        "read_count": 0,
        "write_count": 0,
        "read_bytes": 0,
        "write_bytes": 0,
        "read_time": 0,
        "write_time": 0,
    }


class DiskMonitor:
    """Class wrapper for Disk storage partition and I/O hardware metrics."""

    def __init__(self) -> None:
        logger.info("disk_monitor_initialized")

    def get_disk_partitions(self) -> List[Dict[str, Any]]:
        return get_disk_partitions()

    def get_free_space(self, path: str = "/") -> Dict[str, Any]:
        return get_free_space(path)

    def get_disk_usage(self) -> Dict[str, Any]:
        return get_disk_usage()

    def get_disk_io(self) -> Dict[str, Any]:
        return get_disk_io()

    def get_metrics(self) -> Dict[str, Any]:
        """Collects complete disk storage metrics dictionary."""
        usage = get_disk_usage()
        io = get_disk_io()
        return {
            "total_bytes": usage["total"],
            "used_bytes": usage["used"],
            "free_bytes": usage["free"],
            "percent": usage["percent"],
            "read_bytes": io["read_bytes"],
            "write_bytes": io["write_bytes"],
            "partitions": get_disk_partitions(),
        }
