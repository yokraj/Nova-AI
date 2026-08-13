"""Abstract interface contracts for Autonomous Internet & Service Automation."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.ai.services.models import (
    PaymentGuardResult,
    ServiceDefinition,
    ServiceHealth,
    ServiceMetrics,
    ServiceRequest,
    ServiceResult,
)


class IServiceRegistry(ABC):
    """Abstract contract for service definition registry."""

    @abstractmethod
    def register_service(self, service: ServiceDefinition) -> None:
        pass

    @abstractmethod
    def get_service(self, service_id: str) -> Optional[ServiceDefinition]:
        pass

    @abstractmethod
    def list_services(self, category: Optional[str] = None) -> List[ServiceDefinition]:
        pass


class IPaymentGuard(ABC):
    """Abstract contract for payment safety interception."""

    @abstractmethod
    async def verify_payment(self, action_name: str, amount: float, currency: str = "INR") -> PaymentGuardResult:
        pass


class IWorkflowEngine(ABC):
    """Abstract contract for service workflow execution."""

    @abstractmethod
    async def execute_service(self, request: ServiceRequest) -> ServiceResult:
        pass

    @abstractmethod
    async def get_status(self, request_id: str) -> Optional[ServiceResult]:
        pass


class IServiceAutomationPlatform(ABC):
    """Abstract contract for central Service Automation Platform facade."""

    @abstractmethod
    async def execute_service(self, service_id: str, parameters: Dict[str, Any]) -> ServiceResult:
        pass

    @abstractmethod
    async def get_metrics(self) -> ServiceMetrics:
        pass

    @abstractmethod
    def check_health(self) -> ServiceHealth:
        pass
