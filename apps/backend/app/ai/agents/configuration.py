"""Configuration settings schema for Universal Agent Workforce & Autonomous AI Company.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class WorkforceRegistryConfig(BaseModel):
    """Registry capacity metrics model."""

    maximum_agents: int = Field(100)
    registered_agents_count: int = Field(68)


class WorkforceManagerConfig(BaseModel):
    """Workforce manager configuration settings."""

    heartbeat_interval: float = Field(10.0)


class WorkforceConfiguration(BaseModel):
    """System-wide configuration settings for Nova AI Workforce."""

    workforce_name: str = Field("Nova Autonomous AI Workforce", description="Human-readable workforce organization name")
    version: str = Field("3.4.20", description="Agent Workforce version")
    enabled: bool = Field(True, description="Enable autonomous agent workforce execution")
    local_first: bool = Field(True, description="Enforce local-first execution")

    # Division & Capacity Limits
    max_parallel_agents: int = Field(32, description="Maximum concurrent active agents")
    max_task_queue_depth: int = Field(500, description="Task delegation queue capacity limit")
    default_task_timeout_seconds: float = Field(300.0, description="Individual task timeout in seconds")

    # Peer Review & Quality Control
    peer_review_enabled: bool = Field(True, description="Enforce multi-agent peer review quality gates")
    min_approval_score: float = Field(0.85, description="Minimum quality score for peer review approval")
    require_security_audit: bool = Field(True, description="Require security agent signoff on code/system changes")

    # Shared Memory & Learning
    shared_memory_ttl_seconds: int = Field(86400, description="Shared memory item retention TTL")
    learning_engine_enabled: bool = Field(True, description="Enable autonomous pattern and workflow learning")

    # Observability
    telemetry_enabled: bool = Field(True, description="Enable real-time agent telemetry collection")
    heartbeat_interval_seconds: float = Field(5.0, description="Agent bus heartbeat check interval")

    @property
    def registry(self) -> WorkforceRegistryConfig:
        return WorkforceRegistryConfig(maximum_agents=100)

    @property
    def manager(self) -> WorkforceManagerConfig:
        return WorkforceManagerConfig(heartbeat_interval=10.0)


MultiAgentFoundationConfiguration = WorkforceConfiguration


