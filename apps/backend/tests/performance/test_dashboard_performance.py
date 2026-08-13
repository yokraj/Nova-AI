"""Enterprise Dashboard Performance Test Suite.

Profiles latency, throughput, and memory allocations for time-series downsampling,
KPI calculations, notification priority queue operations, and report generation.
"""

from datetime import datetime, timedelta, timezone
import time
import pytest

from app.analytics_engine import AnalyticsAggregator, KPIEngine, TimeSeriesEngine
from app.notification_engine import NotificationQueue


def test_timeseries_downsampling_performance():
    """Profiles downsampling 10,000 time-series samples."""
    ts_engine = TimeSeriesEngine()

    now = datetime.now(timezone.utc)
    samples = [
        {
            "timestamp": (now - timedelta(seconds=i * 5)).isoformat(),
            "value": float(i % 100),
        }
        for i in range(10000)
    ]

    start = time.time()
    hourly_buckets = ts_engine.aggregate_hourly(samples)
    duration_ms = (time.time() - start) * 1000.0

    assert len(hourly_buckets) > 0
    # Must complete downsampling 10,000 items in under 200ms
    assert duration_ms < 200.0


def test_kpi_computation_performance():
    """Profiles KPI calculation speed across 1,000 iterations."""
    kpi_engine = KPIEngine()
    telemetry = {
        "resources": {"cpu_avg": 45.0, "memory_avg": 60.0, "disk_avg": 70.0, "network_bytes_sec": 10485760.0},
        "health": {"average_health_score": 0.95},
        "notifications": {"total_notifications": 120},
        "missions": {"completion_rate_percent": 98.5},
        "agents": {"availability_rate_percent": 95.0},
        "workflows": {"completion_rate_percent": 99.0},
        "system": {"uptime_avg": 86400.0},
    }

    start = time.time()
    for _ in range(1000):
        kpis = kpi_engine.generate_kpis(telemetry)
    duration_ms = (time.time() - start) * 1000.0

    assert kpis["cpu_utilization_percent"] == 45.0
    # 1,000 iterations must complete in under 100ms (<0.1ms per calculation)
    assert duration_ms < 100.0


@pytest.mark.asyncio
async def test_notification_queue_throughput():
    """Profiles priority queue insertion and dequeuing throughput for 1,000 items."""
    queue = NotificationQueue(capacity=5000)

    start = time.time()
    for i in range(1000):
        prio = "URGENT" if i % 10 == 0 else ("HIGH" if i % 4 == 0 else "NORMAL")
        await queue.enqueue({"id": f"notif-{i}", "priority": prio, "title": f"Alert {i}"})
    enqueue_duration_ms = (time.time() - start) * 1000.0

    assert (await queue.size()) == 1000

    start = time.time()
    for _ in range(1000):
        item = await queue.dequeue()
        assert item is not None
    dequeue_duration_ms = (time.time() - start) * 1000.0

    assert (await queue.size()) == 0
    assert enqueue_duration_ms < 150.0
    assert dequeue_duration_ms < 150.0
