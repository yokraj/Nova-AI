"""Unit tests for the Agent SDK Observability SDK.

Verifies JSON logs formatting, metrics counters, trace hierarchies, CPU/Memory telemetry,
profiler elapsed thresholds, health heartbeat logs, audit trails, and dashboard JSON providers.
"""

import asyncio
from datetime import datetime
import pytest

from app.agent_sdk.observability import (
    AuditLogger,
    DashboardProvider,
    EventPublisher,
    HealthMonitor,
    MetricsCollector,
    ObservabilityConfiguration,
    Profiler,
    Span,
    StructuredLogger,
    TelemetryCollector,
    Tracer,
)
from app.runtime.events.event import SystemEvent
from app.runtime.events.event_bus import EventBus
from app.runtime.events.topics import Topic


def test_structured_logging() -> None:
    """Verifies StructuredLogger formats logs without errors."""
    logger = StructuredLogger("ObservabilityAgent")

    # Verify calls do not raise exceptions
    logger.info("Info log message")
    logger.error("Error log message", task_name="TestTask")
    logger.warning("Warning log message")


def test_metrics_collector() -> None:
    """Verifies MetricsCollector logs and latency calculations."""
    collector = MetricsCollector()

    collector.record_execution(duration=1.5, success=True)
    collector.record_execution(duration=2.5, success=False, retries=1)

    assert collector.execution_count == 2
    assert collector.success_count == 1
    assert collector.failure_count == 1
    assert collector.retry_count == 1
    assert collector.average_duration == 2.0


def test_trace_hierarchy_and_nested_spans() -> None:
    """Verifies trace contexts mapping and nested spans parent-child links."""
    tracer = Tracer()

    trace_id = tracer.start_trace()
    assert trace_id is not None

    root_id = tracer.start_span("root_span")
    child_id = tracer.start_span("child_span")

    tracer.finish_span(child_id)
    tracer.finish_span(root_id)
    tracer.finish_trace()

    spans = tracer.get_completed_spans()
    assert len(spans) == 2

    # Child completed first
    child_span = spans[0]
    root_span = spans[1]

    assert child_span.parent_span_id == root_span.span_id
    assert child_span.trace_id == trace_id
    assert root_span.parent_span_id is None


def test_telemetry_collector() -> None:
    """Verifies TelemetryCollector resource snapshots."""
    telemetry = TelemetryCollector()

    telemetry.collect(cpu=12.5, memory=256.0, tokens=100)
    telemetry.collect(cpu=15.0, memory=260.0, tokens=50)

    snapshot = telemetry.snapshot()
    assert snapshot["cpu_usage"] == 15.0
    assert snapshot["memory_usage"] == 260.0
    assert snapshot["token_usage"] == 150


@pytest.mark.anyio
async def test_profiler_timings() -> None:
    """Verifies Profiler timing checks and threshold flags."""
    profiler = Profiler()

    profiler.start()
    await asyncio.sleep(0.1)
    duration = profiler.stop()

    assert duration >= 0.1
    assert profiler.slow_execution_detection(threshold_seconds=0.05) is True
    assert profiler.slow_execution_detection(threshold_seconds=1.0) is False


def test_health_monitoring() -> None:
    """Verifies HealthMonitor statuses and checks counter updates."""
    monitor = HealthMonitor()

    status_healthy = monitor.get_status()
    assert status_healthy["status"] == "healthy"
    assert status_healthy["checks_count"] == 0

    monitor.degraded()
    status_degraded = monitor.get_status()
    assert status_degraded["status"] == "degraded"
    assert status_degraded["checks_count"] == 1

    monitor.unhealthy()
    status_unhealthy = monitor.get_status()
    assert status_unhealthy["status"] == "unhealthy"
    assert status_unhealthy["checks_count"] == 2


def test_audit_logging() -> None:
    """Verifies AuditLogger records permission and config modifications."""
    logger = AuditLogger()

    logger.permission_change("TestAgent", "database", "read", "allow")
    logger.configuration_change("Observability", "enable_logging", True)
    logger.agent_execution("TestAgent", "exec-123", success=True)
    logger.security_event("Authentication", "CRITICAL", "Failed login attempt")

    records = logger.list_records()
    assert len(records) == 4
    assert records[0]["action"] == "permission_change"
    assert records[1]["action"] == "configuration_change"
    assert records[2]["action"] == "agent_execution"
    assert records[3]["action"] == "security_event"


def test_dashboard_provider() -> None:
    """Verifies DashboardProvider exposes timelines and DAG trace formats."""
    tracer = Tracer()
    trace_id = tracer.start_trace()
    root_id = tracer.start_span("root_span")
    tracer.finish_span(root_id)
    tracer.finish_trace()

    monitor = HealthMonitor()
    telemetry = TelemetryCollector()
    telemetry.collect(cpu=10.0, memory=512.0)

    dashboard = DashboardProvider(tracer, monitor, telemetry)

    exec_id = uuid_mock()
    dashboard.record_start(exec_id, "TestAgent", "TaskA")
    assert len(dashboard.active_tasks()) == 1

    dashboard.record_complete(exec_id, success=True, latency=0.5)
    assert len(dashboard.active_tasks()) == 0

    summary = dashboard.summary()
    assert summary["completed_executions"] == 1
    assert summary["average_latency"] == 0.5
    assert summary["health"]["status"] == "healthy"

    timeline = dashboard.execution_timeline()
    assert len(timeline) == 1
    assert timeline[0]["status"] == "completed"

    graph = dashboard.trace_graph()
    assert len(graph["nodes"]) == 1
    assert graph["nodes"][0]["label"] == "root_span"


@pytest.mark.anyio
async def test_event_publishing() -> None:
    """Verifies EventPublisher maps and publishes events onto EventBus."""
    bus = EventBus()
    publisher = EventPublisher(event_bus=bus)

    received_events = []

    async def callback(event: SystemEvent) -> None:
        received_events.append(event)

    bus.subscribe(Topic.AGENT_STARTED, callback)
    bus.subscribe(Topic.AGENT_STOPPED, callback)
    bus.subscribe(Topic.CONVERSATION_UPDATED, callback)
    bus.subscribe(Topic.JOB_STARTED, callback)
    bus.subscribe(Topic.JOB_COMPLETED, callback)
    bus.subscribe(Topic.JOB_FAILED, callback)

    # Publish events
    await publisher.publish_agent_started("MyAgent")
    await publisher.publish_agent_completed("MyAgent")
    await publisher.publish_agent_failed("MyAgent", "agent error")
    await publisher.publish_permission_granted("MyAgent", "filesystem")
    await publisher.publish_permission_denied("MyAgent", "network")
    await publisher.publish_execution_started("exec-1")
    await publisher.publish_execution_completed("exec-1", "exec-result")
    await publisher.publish_execution_failed("exec-1", "exec error")

    # Verify all 8 events published successfully
    assert len(received_events) == 8
    assert received_events[0].topic == Topic.AGENT_STARTED
    assert received_events[1].topic == Topic.AGENT_STOPPED
    assert received_events[1].payload["event_type"] == "AgentCompleted"
    assert received_events[2].payload["error"] == "agent error"
    assert received_events[3].payload["event_type"] == "PermissionGranted"
    assert received_events[4].payload["event_type"] == "PermissionDenied"
    assert received_events[5].payload["event_type"] == "ExecutionStarted"
    assert received_events[6].payload["event_type"] == "ExecutionCompleted"
    assert received_events[7].payload["event_type"] == "ExecutionFailed"


def uuid_mock() -> Any:
    """Return a standard UUID."""
    import uuid

    return uuid.uuid4()
