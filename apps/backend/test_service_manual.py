"""12-Stage Manual Validation Script for M3.3.12 Autonomous Internet & Service Automation Platform."""

import asyncio
import sys
import structlog

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

logger = structlog.get_logger("test_service_manual")


async def run_manual_validation() -> None:
    print("=========================================")
    print("Nova AI Service Automation Validation")
    print("=========================================")

    # Stage 1: Configuration
    config = ServiceConfiguration()
    assert config.enabled is True
    assert config.payment_guard_strict is True
    print("Stage 1  Service Configuration      PASS")

    # Stage 2: Service Registry
    reg = ServiceRegistry()
    services = reg.list_services()
    assert len(services) >= 7
    print("Stage 2  Service Registry           PASS")

    # Stage 3: Website Detection
    detector = WebsiteDetector()
    domain, url = await detector.detect_website("renew my passport")
    assert domain == "passportindia.gov.in"
    print("Stage 3  Website & Route Detection   PASS")

    # Stage 4: Travel Domain Workflows
    train_wf = TrainBookingWorkflow()
    t_res = await train_wf.execute({"source": "Bangalore", "destination": "Chennai"})
    assert t_res["status"] == "seats_available"
    print("Stage 4  Travel Workflows (Train)   PASS")

    # Stage 5: Shopping Domain Workflows
    shop_wf = ProductSearchWorkflow()
    s_res = await shop_wf.execute({"query": "Wireless Earbuds"})
    assert len(s_res["results"]) == 2
    print("Stage 5  Shopping Workflows         PASS")

    # Stage 6: Government Domain Workflows
    govt_wf = PassportRenewalWorkflow()
    g_res = await govt_wf.execute({"applicant_name": "Nova User"})
    assert g_res["portal"] == "Passport Seva Kendra"
    print("Stage 6  Government Workflows       PASS")

    # Stage 7: Finance Workflows & Payment Guard
    fin_wf = FundTransferWorkflow()
    f_res = await fin_wf.execute({"recipient": "John", "amount": 5000.0})
    assert f_res["amount"] == 5000.0
    guard = PaymentGuard()
    p_guard_res = await guard.verify_payment("fund_transfer", 5000.0)
    assert p_guard_res.approved is True
    print("Stage 7  Finance & Payment Guard    PASS")

    # Stage 8: Authentication & Credential Management
    auth_mgr = AuthenticationManager()
    authed = await auth_mgr.ensure_authenticated("train_booking")
    assert authed is True
    print("Stage 8  Authentication & Sessions  PASS")

    # Stage 9: CAPTCHA & OTP Interception
    captcha_mgr = CaptchaDetector()
    c_info = await captcha_mgr.detect_captcha("Recaptcha challenge")
    assert c_info.solved is True
    otp_mgr = OTPHandler()
    otp_req = await otp_mgr.prompt_otp("train_booking")
    assert otp_req.entered_code == "123456"
    print("Stage 9  CAPTCHA & OTP Handling     PASS")

    # Stage 10: End-to-End Workflow Execution
    engine = WorkflowEngine()
    req = ServiceRequest(
        service_id="train_booking",
        category=ServiceType.TRAVEL,
        action_name="book_train",
        parameters={"source": "Bangalore", "destination": "Chennai", "amount": 320.0},
    )
    e_res = await engine.execute_service(req)
    assert e_res.success is True
    print("Stage 10 End-to-End Workflow Engine PASS")

    # Stage 11: Automation & Learning Bridges
    ab = AutomationBridge()
    b_res = await ab.execute_browser_action("navigate", {"url": "https://irctc.co.in"})
    assert b_res["status"] == "success"
    lb = LearningBridge()
    await lb.record_workflow_experience("train_booking", True, 2.5, {})
    print("Stage 11 Automation & Learning Bridges PASS")

    # Stage 12: Gateway Integration
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass
    gateway = resolve(IAIGateway)
    srv_list = await gateway.list_services()
    assert len(srv_list) >= 7
    gw_exec = await gateway.execute_service("train_booking", {"source": "BLR", "destination": "MAA"})
    assert gw_exec["success"] is True
    print("Stage 12 Gateway Integration        PASS")

    print("\n12/12 PASS")
    print("\nService Automation Platform Healthy")


if __name__ == "__main__":
    asyncio.run(run_manual_validation())
