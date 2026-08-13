"""Platform Validation Configuration Module.

Defines Pydantic settings for benchmark thresholds, load testing limits,
security audit parameters, backup directories, and production SLA targets.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ValidationConfig(BaseModel):
    """Configuration settings for Enterprise Platform Validation Suite."""

    # Target SLAs (Latency Bounds in Milliseconds)
    max_memory_crud_latency_ms: float = Field(default=10.0, description="Max SLA latency for Memory CRUD operations")
    max_embedding_latency_ms: float = Field(default=15.0, description="Max SLA latency for Embedding vector generation")
    max_hybrid_rag_latency_ms: float = Field(default=35.0, description="Max SLA latency for Hybrid RAG retrieval")
    max_graph_traversal_latency_ms: float = Field(default=20.0, description="Max SLA latency for Knowledge Graph traversal")
    max_context_assembly_latency_ms: float = Field(default=25.0, description="Max SLA latency for Context Assembly")

    # Load Testing Targets
    stress_test_memories_count: int = Field(default=100000, description="Target memory entries count for load testing")
    stress_test_vectors_count: int = Field(default=100000, description="Target vector count for load testing")
    concurrent_users_limit: int = Field(default=100, description="Target concurrent user load")
    concurrent_requests_target: int = Field(default=1000, description="Target concurrent requests per second")

    # Backup & Security Configuration
    backup_directory: str = Field(default="./data/backups", description="Local persistence path for backups")
    backup_retention_days: int = Field(default=30, description="Retention policy for snapshots")
    strict_tenant_isolation: bool = Field(default=True, description="Enforces strict workspace/project boundary checks")
