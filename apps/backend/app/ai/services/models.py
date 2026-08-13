"""Domain models and data schemas for Autonomous Internet & Service Automation."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ServiceType(str, Enum):
    """Supported service domain categories."""

    TRAVEL = "travel"
    SHOPPING = "shopping"
    GOVERNMENT = "government"
    FINANCE = "finance"
    EDUCATION = "education"
    PRODUCTIVITY = "productivity"
    COMMUNICATION = "communication"
    HEALTHCARE = "healthcare"


class WorkflowState(str, Enum):
    """Lifecycle state of a service workflow."""

    IDLE = "idle"
    NAVIGATING = "navigating"
    AUTHENTICATING = "authenticating"
    AWAITING_OTP = "awaiting_otp"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ---------------------------------------------------------------------------
# Domain Models
# ---------------------------------------------------------------------------

class ServiceDefinition(BaseModel):
    """Metadata specification for a registered service workflow."""

    service_id: str
    name: str
    category: ServiceType
    description: str
    target_domain: str
    requires_auth: bool = False
    requires_payment: bool = False
    voice_triggers: List[str] = Field(default_factory=list)


class CredentialRecord(BaseModel):
    """Secure local user credential model."""

    service_id: str
    username: str
    password_hash: str = ""
    domain: str = ""
    last_used: datetime = Field(default_factory=datetime.utcnow)


class CaptchaInfo(BaseModel):
    """CAPTCHA challenge metadata."""

    captcha_type: str = "recaptcha"
    detected: bool = False
    solved: bool = False
    solution_text: Optional[str] = None


class OTPRequest(BaseModel):
    """OTP code request prompt model."""

    otp_id: str = Field(default_factory=lambda: f"otp_{uuid4().hex[:8]}")
    service_id: str
    prompt_message: str
    timeout_seconds: float = 120.0
    entered_code: Optional[str] = None


class PaymentGuardResult(BaseModel):
    """Result evaluation of financial payment safety guard."""

    action_name: str
    amount: float = 0.0
    currency: str = "INR"
    approved: bool = False
    requires_human_approval: bool = True
    reason: str = ""


class ServiceRequest(BaseModel):
    """User request invocation for internet service automation."""

    request_id: str = Field(default_factory=lambda: f"srv_req_{uuid4().hex[:10]}")
    service_id: str
    category: ServiceType
    action_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    agent_id: str = "system"
    mission_id: Optional[str] = None


class ServiceResult(BaseModel):
    """Output result of a service workflow execution."""

    request_id: str
    service_id: str
    success: bool
    state: WorkflowState = WorkflowState.COMPLETED
    data: Optional[Any] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0
    payment_approved: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ServiceMetrics(BaseModel):
    """Telemetry metrics snapshot for service automation."""

    total_services_executed: int = 0
    successful_services: int = 0
    failed_services: int = 0
    success_rate: float = 0.0
    average_duration_seconds: float = 0.0
    travel_workflows_count: int = 0
    shopping_workflows_count: int = 0
    government_workflows_count: int = 0
    finance_workflows_count: int = 0
    otps_handled_count: int = 0


class ServiceHealth(BaseModel):
    """Composite health state of the service automation platform."""

    status: str = "healthy"
    registered_services_count: int = 0
    active_workflows_count: int = 0
    components: Dict[str, str] = Field(default_factory=dict)
