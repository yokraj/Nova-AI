"""Automated unit test suite verifying Safety Engine operations.
"""

import pytest
from app.ai.gateway import IAIGateway
from app.core.dependency_container import resolve, register_ai_gateway_dependencies
from app.ai.safety.safety_engine import SafetyEngine
from app.ai.safety.exceptions import PermissionDenied
from app.ai.safety.models import RiskLevel

@pytest.mark.anyio
async def test_safety_engine_flows():
    """Verifies action intent evaluations, risk policies blocks, and user decisions loops."""
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)
    engine = SafetyEngine(
        event_bus=gateway.agents.event_bus,
        memory_engine=gateway.memory
    )

    # 1. Test risk classification
    assess_critical = engine.classify_risk("purchase ticket", {"cost_value": "INR 1,250"})
    assert assess_critical.risk_level == RiskLevel.CRITICAL

    assess_high = engine.classify_risk("delete files", {"count_value": "1,240"})
    assert assess_high.risk_level == RiskLevel.HIGH

    assess_no_app = engine.classify_risk("explain code", {})
    assert assess_no_app.risk_level == RiskLevel.NO_APPROVAL

    # 2. Test command expansion blocks
    with pytest.raises(PermissionDenied):
        await engine.check_action("ms_test", "run script; rm -rf /", {})

    # 3. Test policy evaluation and approval pauses
    check_gated = await engine.check_action("ms_test", "delete database", {"count_value": "1"})
    assert check_gated["status"] == "gated"
    app_id = check_gated["approval_id"]

    assert len(engine.pending_approvals()) == 1
    assert engine.pending_approvals()[0].approval_id == app_id

    # Resolve approval
    approved = await engine.approve(app_id)
    assert approved is True
    assert len(engine.pending_approvals()) == 0
    assert len(engine.approval_history()) == 1

    # 4. Test consent manager
    engine.consent.give_consent("delete database")
    check_consented = await engine.check_action("ms_test", "delete database", {"count_value": "1"})
    assert check_consented["status"] == "approved"
    assert check_consented["gated"] is False

    # 5. Test gateway resolution
    res_req = await gateway.request_approval("ms_test", "buy book", {"cost_value": "INR 500"})
    assert res_req["status"] == "gated"
    gateway_app_id = res_req["approval_id"]

    resolved_gateway = await gateway.approve(gateway_app_id)
    assert resolved_gateway is True
