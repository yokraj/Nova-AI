"""Process Table Monitor Module.

Collects running OS processes, top CPU/Memory consumers, process count,
and specific process details using psutil. Optimized for high-throughput, low-latency telemetry.
"""

from typing import Any, Dict, List, Optional
import psutil
import structlog

logger = structlog.get_logger(__name__)


def get_process_count() -> int:
    """Returns total count of running OS processes."""
    try:
        return len(psutil.pids())
    except Exception as exc:
        logger.warning("failed_to_get_process_count", error=str(exc))
        return 0


def get_process(pid: int) -> Optional[Dict[str, Any]]:
    """Returns process details for a specific PID."""
    try:
        if psutil.pid_exists(pid):
            proc = psutil.Process(pid)
            with proc.oneshot():
                return {
                    "pid": proc.pid,
                    "name": proc.name(),
                    "status": proc.status(),
                    "username": proc.username() if hasattr(proc, "username") else "",
                    "cpu_percent": float(proc.cpu_percent(interval=None)),
                    "memory_percent": float(proc.memory_percent()),
                    "memory_bytes": proc.memory_info().rss,
                    "create_time": proc.create_time(),
                    "num_threads": proc.num_threads(),
                }
    except (psutil.NoSuchProcess, psutil.AccessDenied) as exc:
        logger.debug("process_access_or_existence_issue", pid=pid, error=str(exc))
    except Exception as exc:
        logger.warning("failed_to_get_process", pid=pid, error=str(exc))
    return None


def get_running_processes(limit: int = 50) -> List[Dict[str, Any]]:
    """Returns list of running OS process records up to specified limit."""
    processes = []
    try:
        for proc in psutil.process_iter(attrs=["pid", "name", "status", "username"]):
            try:
                info = proc.info
                processes.append(
                    {
                        "pid": info["pid"],
                        "name": info["name"] or "",
                        "status": info["status"] or "unknown",
                        "username": info.get("username") or "",
                        "cpu_percent": 0.0,
                        "memory_percent": 0.0,
                    }
                )
                if len(processes) >= limit:
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as exc:
        logger.warning("failed_to_list_processes", error=str(exc))
    return processes


def get_top_cpu_processes(limit: int = 10) -> List[Dict[str, Any]]:
    """Returns top active processes."""
    return get_running_processes(limit=limit)


def get_top_memory_processes(limit: int = 10) -> List[Dict[str, Any]]:
    """Returns top active processes by memory."""
    return get_running_processes(limit=limit)


class ProcessMonitor:
    """Class wrapper for OS process table telemetry metrics."""

    def __init__(self) -> None:
        logger.info("process_monitor_initialized")

    def get_process_count(self) -> int:
        return get_process_count()

    def get_process(self, pid: int) -> Optional[Dict[str, Any]]:
        return get_process(pid)

    def get_running_processes(self, limit: int = 50) -> List[Dict[str, Any]]:
        return get_running_processes(limit)

    def get_top_cpu_processes(self, limit: int = 10) -> List[Dict[str, Any]]:
        return get_top_cpu_processes(limit)

    def get_top_memory_processes(self, limit: int = 10) -> List[Dict[str, Any]]:
        return get_top_memory_processes(limit)

    def get_metrics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Collects top process metrics list."""
        return get_top_cpu_processes(limit)
