"""CPU Hardware Monitor Module.

Collects real-time CPU usage, per-core percentage, clock frequency, core counts,
temperature sensors, and system load averages using psutil and platform.
Handles OS hardware differences gracefully.
"""

import os
from typing import Dict, List, Optional
import psutil
import structlog

logger = structlog.get_logger(__name__)


def get_cpu_usage() -> float:
    """Returns overall CPU utilization percentage."""
    try:
        return float(psutil.cpu_percent(interval=None))
    except Exception as exc:
        logger.warning("failed_to_get_cpu_usage", error=str(exc))
        return 0.0


def get_cpu_percent_per_core() -> List[float]:
    """Returns CPU utilization percentage per logical core."""
    try:
        return [float(val) for val in psutil.cpu_percent(interval=None, percpu=True)]
    except Exception as exc:
        logger.warning("failed_to_get_cpu_percent_per_core", error=str(exc))
        return []


def get_cpu_frequency() -> Dict[str, float]:
    """Returns CPU current, min, and max clock frequency in MHz."""
    try:
        freq = psutil.cpu_freq()
        if freq:
            return {
                "current": float(freq.current or 0.0),
                "min": float(freq.min or 0.0),
                "max": float(freq.max or 0.0),
            }
    except Exception as exc:
        logger.warning("failed_to_get_cpu_frequency", error=str(exc))
    return {"current": 0.0, "min": 0.0, "max": 0.0}


def get_cpu_count() -> Dict[str, int]:
    """Returns physical and logical CPU core counts."""
    try:
        physical = psutil.cpu_count(logical=False) or 1
        logical = psutil.cpu_count(logical=True) or 1
        return {"physical": physical, "logical": logical}
    except Exception as exc:
        logger.warning("failed_to_get_cpu_count", error=str(exc))
        return {"physical": 1, "logical": 1}


def get_cpu_temperature() -> Optional[float]:
    """Returns CPU temperature in Celsius if sensors are supported on host platform."""
    try:
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        if entry.current:
                            return float(entry.current)
    except Exception as exc:
        logger.debug("cpu_temperature_sensor_unavailable", error=str(exc))
    return None


def get_load_average() -> Dict[str, float]:
    """Returns system load average over 1, 5, and 15 minute intervals."""
    try:
        if hasattr(os, "getloadavg"):
            load1, load5, load15 = os.getloadavg()
            return {"1min": float(load1), "5min": float(load5), "15min": float(load15)}
        elif hasattr(psutil, "getloadavg"):
            load1, load5, load15 = psutil.getloadavg()
            return {"1min": float(load1), "5min": float(load5), "15min": float(load15)}
    except Exception as exc:
        logger.debug("get_load_average_unavailable", error=str(exc))
    return {"1min": 0.0, "5min": 0.0, "15min": 0.0}


class CPUMonitor:
    """Class wrapper for CPU telemetry hardware metrics."""

    def __init__(self) -> None:
        logger.info("cpu_monitor_initialized")

    def get_cpu_usage(self) -> float:
        return get_cpu_usage()

    def get_cpu_percent_per_core(self) -> List[float]:
        return get_cpu_percent_per_core()

    def get_cpu_frequency(self) -> Dict[str, float]:
        return get_cpu_frequency()

    def get_cpu_count(self) -> Dict[str, int]:
        return get_cpu_count()

    def get_cpu_temperature(self) -> Optional[float]:
        return get_cpu_temperature()

    def get_load_average(self) -> Dict[str, float]:
        return get_load_average()

    def get_metrics(self) -> Dict[str, float]:
        """Collects complete CPU metrics dictionary."""
        return {
            "usage_percent": get_cpu_usage(),
            "temperature_celsius": get_cpu_temperature(),
            "load_1min": get_load_average()["1min"],
            "cores_logical": float(get_cpu_count()["logical"]),
            "frequency_mhz": get_cpu_frequency()["current"],
        }
