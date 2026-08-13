"""Configuration settings and schemas for Universal Device Mesh, Edge AI & Cross-Platform Orchestration Platform.
"""

from typing import Any, Dict
from pydantic import BaseModel, Field


class DeviceMeshConfiguration(BaseModel):
    """Configuration schema for Universal Device Mesh."""

    discovery_enabled: bool = Field(True, description="Enable local network mDNS/SSDP peer device discovery")
    heartbeat_interval_sec: float = Field(5.0, description="Node heartbeat check interval in seconds")
    auto_failover_enabled: bool = Field(True, description="Automatically failover tasks to standby mesh nodes upon failure")
    default_encryption_protocol: str = Field("TLS_1_3", description="Inter-node communication encryption protocol")
    storage_dir: str = Field("./data/mesh_devices", description="Directory for node state and pairings")
    cache_ttl_seconds: int = Field(3600, description="Cache TTL for mesh telemetry and device queries")
    extra_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional mesh network configuration settings")
