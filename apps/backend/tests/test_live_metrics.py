"""Unit and Integration Test Suite for Nova AI Enterprise Live Metrics Engine.

Tests LiveMetricsEngine lifecycle, ChangeDetector thresholds, SnapshotManager ring buffer,
MetricsBuffer queueing, MetricsRateLimiter sliding window, MetricsPublisher broadcasting,
MetricsScheduler async loops, and MetricsStatistics telemetry tracking.
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.websockets import WebSocketState

from app.live_metrics import (
    ChangeDetector,
    LiveMetricsConfig,
    LiveMetricsEngine,
    MetricsBuffer,
    MetricsPublisher,
    MetricsRateLimiter,
    MetricsScheduler,
    MetricsStatistics,
    SnapshotManager,
)
from app.websocket.broadcaster import DashboardBroadcaster
from app.websocket.connection import WebSocketConnection
from app.websocket.manager import ConnectionManager


def test_live_metrics_config():
    """Test LiveMetricsConfig initialization and default values."""
    config = LiveMetricsConfig()
    assert config.metrics_interval == 1.0
    assert config.buffer_size == 100
    assert config.publish_rate == 10.0
    assert config.change_threshold == 0.01

    custom_cfg = LiveMetricsConfig.from_dashboard_config({"metrics_interval": 2.5, "buffer_size": 250})
    assert custom_cfg.metrics_interval == 2.5
    assert custom_cfg.buffer_size == 250


def test_snapshot_manager():
    """Test SnapshotManager capture, ring buffer retention, and diffing."""
    mgr = SnapshotManager(max_retention=3)

    snap1 = mgr.capture_snapshot({"cpu": 10.0, "ram": 50.0})
    assert mgr.get_latest_snapshot() == snap1
    assert mgr.get_previous_snapshot() is None

    snap2 = mgr.capture_snapshot({"cpu": 15.0, "ram": 50.0})
    assert mgr.get_previous_snapshot() == snap1
    assert mgr.get_latest_snapshot() == snap2

    # Compare snapshots
    diff = mgr.compare_snapshots(snap2, snap1)
    assert diff["has_changed"] is True
    assert "cpu" in diff["changed_fields"]
    assert diff["deltas"]["cpu"] == 5.0

    # Test ring buffer eviction
    mgr.capture_snapshot({"cpu": 20.0})
    mgr.capture_snapshot({"cpu": 25.0})
    assert len(mgr._snapshots) == 3


def test_change_detector():
    """Test ChangeDetector delta threshold comparisons."""
    detector = ChangeDetector(threshold=0.05)  # 5% threshold

    # 1. 2% CPU change -> False
    assert detector.has_changed({"cpu": 50.0}, {"cpu": 50.5}) is False

    # 2. 10% CPU change -> True
    assert detector.has_changed({"cpu": 50.0}, {"cpu": 56.0}) is True

    # 3. Health status change -> True
    assert detector.compare_health({"status": "degraded"}, {"status": "healthy"}) is True
    assert detector.compare_health({"status": "healthy"}, {"status": "healthy"}) is False


def test_metrics_buffer():
    """Test MetricsBuffer pushing, popping, peeking, and flushing."""
    buf = MetricsBuffer(capacity=5)

    buf.push({"id": 1})
    buf.push({"id": 2})
    buf.push({"id": 3})

    assert buf.size() == 3
    assert buf.peek() == {"id": 1}

    item = buf.pop()
    assert item == {"id": 1}
    assert buf.size() == 2

    flushed = buf.flush()
    assert len(flushed) == 2
    assert buf.size() == 0


def test_metrics_rate_limiter():
    """Test MetricsRateLimiter window rate limits."""
    limiter = MetricsRateLimiter(max_rate_per_sec=2.0, window_seconds=1.0)

    assert limiter.allow_publish("cpu") is True
    limiter.record_publish("cpu")

    assert limiter.allow_publish("cpu") is True
    limiter.record_publish("cpu")

    # 3rd publish in same window exceeds rate of 2.0
    assert limiter.allow_publish("cpu") is False

    limiter.reset()
    assert limiter.allow_publish("cpu") is True


def test_metrics_statistics():
    """Test MetricsStatistics telemetry tracking."""
    stats = MetricsStatistics()

    stats.record_collection(duration_ms=12.5)
    stats.record_broadcast("resources", duration_ms=5.0)
    stats.record_skipped("resources")

    summary = stats.get_summary(connected_clients=10)
    assert summary["collection_count"] == 1
    assert summary["broadcast_count"] == 1
    assert summary["skipped_updates"] == 1
    assert summary["connected_clients"] == 10
    assert summary["channel_statistics"]["resources"]["broadcasts"] == 1


async def test_metrics_scheduler_lifecycle():
    """Test MetricsScheduler start, pause, resume, and stop async loops."""
    counter = 0

    async def sample_callback():
        nonlocal counter
        counter += 1

    scheduler = MetricsScheduler(
        collection_callback=sample_callback,
        collection_interval=0.05,
    )

    scheduler.start()
    assert scheduler.is_running is True

    await asyncio.sleep(0.12)
    assert counter >= 2

    scheduler.pause()
    assert scheduler.is_paused is True
    current_val = counter
    await asyncio.sleep(0.1)
    assert counter == current_val

    scheduler.resume()
    assert scheduler.is_paused is False
    await asyncio.sleep(0.1)
    assert counter > current_val

    scheduler.stop()
    assert scheduler.is_running is False


async def test_live_metrics_engine_workflow():
    """Test LiveMetricsEngine end-to-end collection, diffing, rate limiting, and publishing."""
    conn_mgr = ConnectionManager()
    broadcaster = DashboardBroadcaster(manager=conn_mgr)

    mock_ws = MagicMock()
    mock_ws.client_state = WebSocketState.CONNECTED
    mock_ws.send_json = AsyncMock()

    conn = WebSocketConnection(websocket=mock_ws, user_id="admin-123")
    await conn_mgr.connect(conn)
    conn_mgr.subscribe(conn.connection_id, "resources")

    engine = LiveMetricsEngine(
        connection_manager=conn_mgr,
        broadcaster=broadcaster,
    )

    # 1. First collection cycle -> publishes initial metrics
    metrics1 = await engine.collect_metrics()
    assert "resources" in metrics1
    await engine.publish_metrics(metrics1)

    assert mock_ws.send_json.called

    # Reset mock call count
    mock_ws.send_json.reset_mock()

    # 2. Duplicate metric publish -> skipped by ChangeDetector
    # Store second snapshot with identical data
    engine.snapshot_manager.capture_snapshot(metrics1)
    await engine.publish_metrics(metrics1)
    assert not mock_ws.send_json.called

    # Check statistics
    summary = engine.statistics.get_summary(connected_clients=1)
    assert summary["collection_count"] == 1
    assert summary["skipped_updates"] >= 1
