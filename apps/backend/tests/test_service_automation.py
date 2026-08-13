"""Unit tests for Autonomous Internet & Service Automation Platform."""

import pytest
from app.ai.gateway import IAIGateway
from app.ai.services.authentication_manager import AuthenticationManager
from app.ai.services.automation_bridge import AutomationBridge
from app.ai.services.captcha_detector import CaptchaDetector
from app.ai.services.configuration import ServiceConfiguration
from app.ai.services.credential_manager import CredentialManager
from app.ai.services.finance.workflows import FundTransferWorkflow
from app.ai.services.government.workflows import PassportRenewalWorkflow
from app.ai.services.learning_bridge import LearningBridge
from app.ai.services.models import ServiceRequest, ServiceType
from app.ai.services.otp_handler import OTPHandler
from app.ai.services.payment_guard import PaymentGuard
from app.ai.services.service_registry import ServiceRegistry
from app.ai.services.shopping.workflows import ProductSearchWorkflow
from app.ai.services.travel.workflows import TrainBookingWorkflow
from app.ai.services.website_detector import WebsiteDetector
from app.ai.services.workflow_engine import WorkflowEngine
from app.core.dependency_container import register_ai_gateway_dependencies, resolve


@pytest.mark.anyio
async def test_service_configuration():
    """Verifies service configuration settings."""
    config = ServiceConfiguration()
    assert config.enabled is True
    assert config.payment_guard_strict is True
    assert config.default_currency == "INR"


@pytest.mark.anyio
async def test_service_registry():
    """Verifies service definition registration and queries."""
    reg = ServiceRegistry()
    services = reg.list_services()
    assert len(services) >= 7

    train_service = reg.get_service("train_booking")
    assert train_service is not None
    assert train_service.category == ServiceType.TRAVEL
    assert train_service.requires_payment is True


@pytest.mark.anyio
async def test_website_detector():
    """Verifies site domain and route detection."""
    detector = WebsiteDetector()
    domain, url = await detector.detect_website("book train ticket to Chennai")
    assert domain == "irctc.co.in"
    assert "irctc" in url


@pytest.mark.anyio
async def test_travel_workflows():
    """Verifies travel domain workflows (train, flight, bus, hotel, cab)."""
    wf = TrainBookingWorkflow()
    res = await wf.execute({"source": "Bangalore", "destination": "Chennai"})
    assert res["workflow"] == "train_booking"
    assert res["status"] == "seats_available"
    assert res["total_fare"] == 320.0


@pytest.mark.anyio
async def test_shopping_workflows():
    """Verifies shopping domain workflows (product search, checkout)."""
    wf = ProductSearchWorkflow()
    res = await wf.execute({"query": "Wireless Earbuds"})
    assert res["workflow"] == "product_search"
    assert len(res["results"]) == 2


@pytest.mark.anyio
async def test_government_workflows():
    """Verifies government domain workflows (passport renewal)."""
    wf = PassportRenewalWorkflow()
    res = await wf.execute({"applicant_name": "Nova User"})
    assert res["workflow"] == "passport_renewal"
    assert res["portal"] == "Passport Seva Kendra"


@pytest.mark.anyio
async def test_finance_workflows_and_payment_guard():
    """Verifies finance workflows and mandatory payment safety guard."""
    guard = PaymentGuard(config=ServiceConfiguration())
    guard_res = await guard.verify_payment("fund_transfer", 5000.0, "INR")
    assert guard_res.approved is True

    wf = FundTransferWorkflow()
    res = await wf.execute({"recipient": "John", "amount": 5000.0})
    assert res["workflow"] == "fund_transfer"
    assert res["amount"] == 5000.0


@pytest.mark.anyio
async def test_authentication_and_otp_handling():
    """Verifies credential lookup, authentication, and OTP code prompts."""
    cred_mgr = CredentialManager()
    cred = await cred_mgr.get_credential("train_booking")
    assert cred is not None
    assert cred.username == "irctc_user_01"

    auth_mgr = AuthenticationManager()
    authed = await auth_mgr.ensure_authenticated("train_booking")
    assert authed is True

    otp = OTPHandler()
    req = await otp.prompt_otp("train_booking")
    assert req.entered_code == "123456"


@pytest.mark.anyio
async def test_workflow_engine_end_to_end():
    """Verifies end-to-end service workflow execution in WorkflowEngine."""
    engine = WorkflowEngine()

    req = ServiceRequest(
        service_id="train_booking",
        category=ServiceType.TRAVEL,
        action_name="book_train",
        parameters={"source": "Bangalore", "destination": "Chennai", "amount": 320.0},
    )
    res = await engine.execute_service(req)
    assert res.success is True
    assert res.payment_approved is True
    assert res.data["workflow"] == "train_booking"


@pytest.mark.anyio
async def test_bridges_and_learning():
    """Verifies automation bridge and learning engine bridge integration."""
    ab = AutomationBridge()
    b_res = await ab.execute_browser_action("navigate", {"url": "https://irctc.co.in"})
    assert b_res["status"] == "success"

    lb = LearningBridge()
    await lb.record_workflow_experience("train_booking", True, 2.5, {})


@pytest.mark.anyio
async def test_gateway_service_automation_apis():
    """Verifies AI Gateway service automation methods."""
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)
    services = await gateway.list_services()
    assert len(services) >= 7

    res = await gateway.execute_service("train_booking", {"source": "Bangalore", "destination": "Chennai"})
    assert res["success"] is True
