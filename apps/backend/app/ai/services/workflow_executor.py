"""Workflow Executor executing multi-step service domain workflows."""

from typing import Any, Dict
import structlog

from app.ai.services.finance.workflows import (
    BalanceLookupWorkflow,
    BillPaymentWorkflow,
    FundTransferWorkflow,
    StatementDownloadWorkflow,
)
from app.ai.services.government.workflows import (
    CertificateApplicationWorkflow,
    PassportRenewalWorkflow,
    TaxPortalWorkflow,
)
from app.ai.services.shopping.workflows import (
    CartCheckoutWorkflow,
    OrderTrackerWorkflow,
    PriceComparatorWorkflow,
    ProductSearchWorkflow,
)
from app.ai.services.travel.workflows import (
    BusBookingWorkflow,
    CabBookingWorkflow,
    FlightBookingWorkflow,
    HotelBookingWorkflow,
    TrainBookingWorkflow,
)

logger = structlog.get_logger("workflow_executor")


class WorkflowExecutor:
    """Executes target domain workflow step logic asynchronously."""

    def __init__(self) -> None:
        self._workflows: Dict[str, Any] = {
            "train_booking": TrainBookingWorkflow(),
            "flight_booking": FlightBookingWorkflow(),
            "bus_booking": BusBookingWorkflow(),
            "hotel_booking": HotelBookingWorkflow(),
            "cab_booking": CabBookingWorkflow(),
            "product_search": ProductSearchWorkflow(),
            "price_comparison": PriceComparatorWorkflow(),
            "order_tracker": OrderTrackerWorkflow(),
            "cart_checkout": CartCheckoutWorkflow(),
            "passport_renewal": PassportRenewalWorkflow(),
            "tax_portal": TaxPortalWorkflow(),
            "certificate_application": CertificateApplicationWorkflow(),
            "balance_lookup": BalanceLookupWorkflow(),
            "bill_payment": BillPaymentWorkflow(),
            "fund_transfer": FundTransferWorkflow(),
            "statement_download": StatementDownloadWorkflow(),
        }

    async def execute_steps(self, service_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute domain workflow step runner."""
        wf = self._workflows.get(service_id)
        if wf and hasattr(wf, "execute"):
            return await wf.execute(parameters)
        logger.info("Executing default service workflow fallback", service_id=service_id)
        return {"service_id": service_id, "status": "completed", "params": parameters}
