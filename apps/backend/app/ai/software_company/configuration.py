"""Configuration settings schema for Autonomous AI Software Engineering Company & End-to-End Project Factory.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SoftwareCompanyConfiguration(BaseModel):
    """System-wide configuration settings for Nova AI Software Engineering Company."""

    company_name: str = Field("Nova Autonomous Software Engineering Co.", description="Human-readable company name")
    version: str = Field("3.4.21", description="Software Factory version")
    enabled: bool = Field(True, description="Enable autonomous software company execution")
    local_first: bool = Field(True, description="Enforce local-first execution")

    # Default Tech Stack
    default_backend_framework: str = Field("FastAPI", description="Default backend framework")
    default_frontend_framework: str = Field("React", description="Default frontend framework")
    default_database: str = Field("PostgreSQL", description="Default database engine")
    default_deployment_target: str = Field("Docker", description="Default deployment environment")

    # Factory Pipeline Limits
    max_autofix_attempts: int = Field(3, description="Maximum automated bug fix attempts before escalation")
    enforce_unit_test_coverage_percent: float = Field(85.0, description="Minimum unit test coverage threshold")
    require_architecture_signoff: bool = Field(True, description="Require Solution Architect signoff before coding")
    require_security_review: bool = Field(True, description="Require Security Review signoff before deployment")

    # Memory & Analytics
    project_memory_ttl_days: int = Field(365, description="Continuous project memory retention TTL in days")
    telemetry_enabled: bool = Field(True, description="Enable project factory telemetry")
