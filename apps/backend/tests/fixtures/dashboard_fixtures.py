"""Dashboard Fixtures & Data Generators.

Provides test fixtures for telemetry payloads, authenticated user contexts,
mock WebSocket connection objects, and database session mocks.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List
import uuid


def get_mock_telemetry_payload() -> Dict[str, Any]:
    """Generates a standard raw telemetry payload dictionary."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "resources": [
            {
                "cpu_percent": 42.5,
                "memory_percent": 64.0,
                "disk_percent": 55.0,
                "gpu_percent": 15.0,
                "network_bytes_sec": 5242880.0,
            },
            {
                "cpu_percent": 48.0,
                "memory_percent": 68.0,
                "disk_percent": 55.0,
                "gpu_percent": 18.0,
                "network_bytes_sec": 6291456.0,
            },
        ],
        "health": [
            {
                "component": "system_core",
                "health_score": 0.98,
                "status": "healthy",
            },
            {
                "component": "database",
                "health_score": 0.95,
                "status": "healthy",
            },
        ],
        "notifications": [
            {
                "id": str(uuid.uuid4()),
                "title": "Normal Operation",
                "category": "system",
                "priority": "NORMAL",
                "read": True,
            },
            {
                "id": str(uuid.uuid4()),
                "title": "High Resource Usage Warning",
                "category": "resources",
                "priority": "HIGH",
                "read": False,
            },
        ],
        "agents": [
            {"agent_id": "agent-1", "name": "PlannerAgent", "status": "active"},
            {"agent_id": "agent-2", "name": "CoderAgent", "status": "busy"},
            {"agent_id": "agent-3", "name": "TestAgent", "status": "idle"},
        ],
        "missions": [
            {"mission_id": "m-101", "name": "Build Dashboard", "status": "completed"},
            {"mission_id": "m-102", "name": "Test Security", "status": "running"},
        ],
        "workflows": [
            {"workflow_id": "wf-1", "completion_rate_percent": 99.5},
        ],
        "system": [
            {"uptime": 172800.0, "node_name": "nova-primary-node"},
        ],
    }


def get_mock_user_context(role: str = "admin") -> Dict[str, Any]:
    """Generates user authentication context dictionary."""
    return {
        "user_id": f"user-{uuid.uuid4().hex[:8]}",
        "username": f"user_{role}",
        "role": role,
        "ip_address": "127.0.0.1",
        "user_agent": "PyTest-Enterprise-Runner/1.0",
    }
