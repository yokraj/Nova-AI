"""GPU Hardware Monitor Module.

Collects attached GPU device utilization, VRAM memory usage, thermal metrics,
and power consumption using GPUtil or pynvml.
Gracefully degrades with empty collections when no GPU hardware is installed.
"""

from typing import Any, Dict, List
import structlog

logger = structlog.get_logger(__name__)


def _query_gpu_devices() -> List[Dict[str, Any]]:
    """Queries GPU devices using GPUtil or pynvml with safe fallback."""
    devices = []
    # 1. Try GPUtil
    try:
        import GPUtil

        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            devices.append(
                {
                    "device_index": gpu.id,
                    "name": gpu.name,
                    "uuid": getattr(gpu, "uuid", f"GPU-{gpu.id}"),
                    "load_percent": float(gpu.load * 100.0),
                    "memory_total_mb": float(gpu.memoryTotal),
                    "memory_used_mb": float(gpu.memoryUsed),
                    "memory_free_mb": float(gpu.memoryFree),
                    "memory_percent": float((gpu.memoryUsed / gpu.memoryTotal * 100.0) if gpu.memoryTotal > 0 else 0.0),
                    "temperature_celsius": float(gpu.temperature) if gpu.temperature else 0.0,
                    "power_watts": 0.0,
                }
            )
        if devices:
            return devices
    except Exception as exc:
        logger.debug("gputil_query_failed_or_missing", error=str(exc))

    # 2. Try pynvml fallback
    try:
        import pynvml

        pynvml.nvmlInit()
        count = pynvml.nvmlDeviceGetCount()
        for i in range(count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode("utf-8")
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            try:
                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
            except Exception:
                power = 0.0

            total_mb = float(mem.total / 1024 / 1024)
            used_mb = float(mem.used / 1024 / 1024)
            free_mb = float(mem.free / 1024 / 1024)

            devices.append(
                {
                    "device_index": i,
                    "name": name,
                    "uuid": f"GPU-{i}",
                    "load_percent": float(util.gpu),
                    "memory_total_mb": total_mb,
                    "memory_used_mb": used_mb,
                    "memory_free_mb": free_mb,
                    "memory_percent": float((used_mb / total_mb * 100.0) if total_mb > 0 else 0.0),
                    "temperature_celsius": float(temp),
                    "power_watts": float(power),
                }
            )
    except Exception as exc:
        logger.debug("pynvml_query_failed_or_no_gpu", error=str(exc))

    return devices


def get_gpu_devices() -> List[Dict[str, Any]]:
    """Returns list of all detected GPU device records."""
    return _query_gpu_devices()


def get_gpu_usage() -> List[Dict[str, Any]]:
    """Returns GPU engine compute utilization percentages."""
    return [
        {"device_index": d["device_index"], "name": d["name"], "load_percent": d["load_percent"]}
        for d in get_gpu_devices()
    ]


def get_gpu_temperature() -> List[Dict[str, Any]]:
    """Returns GPU thermal sensor readings in Celsius."""
    return [
        {"device_index": d["device_index"], "name": d["name"], "temperature_celsius": d["temperature_celsius"]}
        for d in get_gpu_devices()
    ]


def get_gpu_memory() -> List[Dict[str, Any]]:
    """Returns VRAM utilization and memory allocations."""
    return [
        {
            "device_index": d["device_index"],
            "name": d["name"],
            "memory_total_mb": d["memory_total_mb"],
            "memory_used_mb": d["memory_used_mb"],
            "memory_free_mb": d["memory_free_mb"],
            "memory_percent": d["memory_percent"],
        }
        for d in get_gpu_devices()
    ]


def get_gpu_power() -> List[Dict[str, Any]]:
    """Returns GPU power draw readings in Watts."""
    return [
        {"device_index": d["device_index"], "name": d["name"], "power_watts": d["power_watts"]}
        for d in get_gpu_devices()
    ]


class GPUMonitor:
    """Class wrapper for GPU hardware telemetry metrics."""

    def __init__(self) -> None:
        logger.info("gpu_monitor_initialized")

    def get_gpu_devices(self) -> List[Dict[str, Any]]:
        return get_gpu_devices()

    def get_gpu_usage(self) -> List[Dict[str, Any]]:
        return get_gpu_usage()

    def get_gpu_temperature(self) -> List[Dict[str, Any]]:
        return get_gpu_temperature()

    def get_gpu_memory(self) -> List[Dict[str, Any]]:
        return get_gpu_memory()

    def get_gpu_power(self) -> List[Dict[str, Any]]:
        return get_gpu_power()

    def get_metrics(self) -> List[Dict[str, Any]]:
        """Collects complete GPU devices metrics list."""
        return get_gpu_devices()
