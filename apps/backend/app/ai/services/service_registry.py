"""Service Registry registering definitions and workflows across domain categories."""

from typing import Dict, List, Optional
import structlog

from app.ai.services.interfaces import IServiceRegistry
from app.ai.services.models import ServiceDefinition, ServiceType

logger = structlog.get_logger("service_registry")


class ServiceRegistry(IServiceRegistry):
    """Central registry of supported internet service workflows."""

    def __init__(self) -> None:
        self._services: Dict[str, ServiceDefinition] = {}
        self._seed_default_services()

    def _seed_default_services(self) -> None:
        """Seed default service definitions."""
        defaults = [
            ServiceDefinition(
                service_id="train_booking",
                name="Train Ticket Booking",
                category=ServiceType.TRAVEL,
                description="Book IRCTC railway tickets",
                target_domain="irctc.co.in",
                requires_auth=True,
                requires_payment=True,
                voice_triggers=["book train", "train ticket", "irctc train"],
            ),
            ServiceDefinition(
                service_id="flight_booking",
                name="Flight Ticket Booking",
                category=ServiceType.TRAVEL,
                description="Book airline flights",
                target_domain="makemytrip.com",
                requires_auth=True,
                requires_payment=True,
                voice_triggers=["book flight", "flight ticket"],
            ),
            ServiceDefinition(
                service_id="product_search",
                name="E-Commerce Product Search",
                category=ServiceType.SHOPPING,
                description="Search products across online stores",
                target_domain="amazon.in",
                requires_auth=False,
                requires_payment=False,
                voice_triggers=["search product", "find item"],
            ),
            ServiceDefinition(
                service_id="cart_checkout",
                name="Cart Checkout & Purchase",
                category=ServiceType.SHOPPING,
                description="Checkout shopping cart",
                target_domain="amazon.in",
                requires_auth=True,
                requires_payment=True,
                voice_triggers=["checkout cart", "buy now"],
            ),
            ServiceDefinition(
                service_id="passport_renewal",
                name="Passport Renewal Application",
                category=ServiceType.GOVERNMENT,
                description="Apply for passport renewal",
                target_domain="passportindia.gov.in",
                requires_auth=True,
                requires_payment=True,
                voice_triggers=["renew passport", "passport application"],
            ),
            ServiceDefinition(
                service_id="bill_payment",
                name="Utility Bill Payment",
                category=ServiceType.FINANCE,
                description="Pay electricity/water/internet bills",
                target_domain="bbps.org.in",
                requires_auth=True,
                requires_payment=True,
                voice_triggers=["pay bill", "electricity bill"],
            ),
            ServiceDefinition(
                service_id="fund_transfer",
                name="Bank Fund Transfer",
                category=ServiceType.FINANCE,
                description="Transfer funds via UPI/NEFT",
                target_domain="netbanking.com",
                requires_auth=True,
                requires_payment=True,
                voice_triggers=["send money", "transfer funds"],
            ),
        ]
        for s in defaults:
            self.register_service(s)

    def register_service(self, service: ServiceDefinition) -> None:
        """Register service definition."""
        self._services[service.service_id] = service
        logger.info("Registered service definition", id=service.service_id, category=service.category)

    def get_service(self, service_id: str) -> Optional[ServiceDefinition]:
        """Lookup service definition."""
        return self._services.get(service_id)

    def list_services(self, category: Optional[str] = None) -> List[ServiceDefinition]:
        """List registered services."""
        if category:
            return [s for s in self._services.values() if s.category.value == category]
        return list(self._services.values())
