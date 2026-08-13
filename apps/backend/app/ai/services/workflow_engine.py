"""Workflow Engine orchestrating site detection, navigation, authentication, OTP, form filling, payment safety, and learning."""

from typing import Any, Dict, Optional
import time
import structlog

from app.ai.services.authentication_manager import AuthenticationManager
from app.ai.services.captcha_detector import CaptchaDetector
from app.ai.services.confirmation_manager import ConfirmationManager
from app.ai.services.exceptions import ServiceNotFoundError
from app.ai.services.interfaces import IWorkflowEngine
from app.ai.services.models import ServiceRequest, ServiceResult, WorkflowState
from app.ai.services.otp_handler import OTPHandler
from app.ai.services.payment_guard import PaymentGuard
from app.ai.services.recovery_manager import RecoveryManager
from app.ai.services.service_registry import ServiceRegistry
from app.ai.services.website_detector import WebsiteDetector
from app.ai.services.workflow_executor import WorkflowExecutor
from app.ai.services.workflow_validator import WorkflowValidator

logger = structlog.get_logger("workflow_engine")


class WorkflowEngine(IWorkflowEngine):
    """Orchestrates end-to-end internet service workflows with safety guards and recovery."""

    def __init__(self) -> None:
        self.registry = ServiceRegistry()
        self.detector = WebsiteDetector()
        self.auth = AuthenticationManager()
        self.captcha = CaptchaDetector()
        self.otp = OTPHandler()
        self.confirmation = ConfirmationManager()
        self.payment = PaymentGuard()
        self.validator = WorkflowValidator()
        self.executor = WorkflowExecutor()
        self.recovery = RecoveryManager()
        self._statuses: Dict[str, ServiceResult] = {}

    async def execute_service(self, request: ServiceRequest) -> ServiceResult:
        """Execute a service workflow request end-to-end."""
        start_time = time.perf_counter()
        logger.info("WorkflowEngine executing request", id=request.request_id, service_id=request.service_id)

        service_def = self.registry.get_service(request.service_id)
        if not service_def:
            # Fallback auto-registration or raise
            raise ServiceNotFoundError(f"Service '{request.service_id}' not found in registry.")

        try:
            # 1. Validate inputs
            await self.validator.validate_request(service_def, request.parameters)

            # 2. Detect target site domain & route
            domain, start_url = await self.detector.detect_website(request.service_id)

            # 3. Ensure Authentication if required
            if service_def.requires_auth:
                await self.auth.ensure_authenticated(request.service_id)

            # 4. Mandatory Payment Safety Guard if financial transaction
            payment_approved = False
            if service_def.requires_payment:
                amount = float(request.parameters.get("amount", 320.0))
                p_res = await self.payment.verify_payment(request.action_name, amount)
                payment_approved = p_res.approved

            # 5. Handle CAPTCHA / OTP if required
            captcha_info = await self.captcha.detect_captcha()
            if service_def.requires_auth:
                await self.otp.prompt_otp(request.service_id)

            # 6. Execute domain workflow steps
            step_data = await self.executor.execute_steps(request.service_id, request.parameters)

            duration = time.perf_counter() - start_time
            result = ServiceResult(
                request_id=request.request_id,
                service_id=request.service_id,
                success=True,
                state=WorkflowState.COMPLETED,
                data=step_data,
                duration_seconds=duration,
                payment_approved=payment_approved,
            )
            self._statuses[request.request_id] = result
            return result

        except Exception as e:
            duration = time.perf_counter() - start_time
            logger.error("WorkflowEngine execution failed, initiating recovery", id=request.request_id, error=str(e))
            rec_data = await self.recovery.recover(request.service_id, e, request.parameters)
            result = ServiceResult(
                request_id=request.request_id,
                service_id=request.service_id,
                success=False,
                state=WorkflowState.FAILED,
                error=str(e),
                data=rec_data,
                duration_seconds=duration,
            )
            self._statuses[request.request_id] = result
            return result

    async def get_status(self, request_id: str) -> Optional[ServiceResult]:
        """Query status of a service workflow request."""
        return self._statuses.get(request_id)
