"""Central Safety Engine coordinating action evaluations and approvals.
"""

import time
import structlog
from typing import Dict, Any, List, Optional
from app.ai.safety.configuration import SafetyConfiguration
from app.ai.safety.exceptions import PermissionDenied
from app.ai.safety.models import RiskLevel, RiskAssessment, ApprovalItem, AuditRecord
from app.ai.safety.risk_classifier import RiskClassifier
from app.ai.safety.policy_engine import PolicyEngine
from app.ai.safety.action_validator import ActionValidator
from app.ai.safety.permission_manager import PermissionManager
from app.ai.safety.consent_manager import ConsentManager
from app.ai.safety.approval_queue import ApprovalQueue
from app.ai.safety.approval_history import ApprovalHistory
from app.ai.safety.approval_manager import ApprovalManager
from app.ai.safety.confirmation_manager import ConfirmationManager
from app.ai.safety.audit_logger import AuditLogger
from app.ai.safety.notification_manager import NotificationManager
from app.ai.safety.event_bridge import SafetyEventBridge
from app.ai.safety.memory import SafetyMemory
from app.ai.safety.metrics import SafetyMetricsTracker
from app.ai.safety.health import SafetyHealthMonitor
from app.ai.safety.providers.mock_provider import MockSafetyProvider

logger = structlog.get_logger("safety_engine")

class SafetyEngine:
    """The central Safety & Human Approval coordinator blocking dangerous actions."""

    def __init__(self, event_bus: Any = None, memory_engine: Any = None) -> None:
        self.config = SafetyConfiguration()
        self.classifier = RiskClassifier()
        self.policy = PolicyEngine()
        self.validator = ActionValidator()
        self.permissions = PermissionManager()
        self.consent = ConsentManager()
        self.queue = ApprovalQueue()
        self.history = ApprovalHistory()
        self.manager = ApprovalManager(self.queue, self.history)
        self.confirmation = ConfirmationManager()
        self.audit = AuditLogger()
        self.notification = NotificationManager(event_bus)
        self.event_bridge = SafetyEventBridge(event_bus)
        self.memory = SafetyMemory(memory_engine)
        self.metrics = SafetyMetricsTracker()
        self.health = SafetyHealthMonitor(self.queue, self.policy, self.consent, self.audit)
        self.mock = MockSafetyProvider()

    def classify_risk(self, action: str, parameters: Dict[str, Any]) -> RiskAssessment:
        """Classifies action intent returning risk levels and reasons."""
        return self.classifier.classify(action, parameters)

    def validate_action(self, action: str, parameters: Dict[str, Any]) -> bool:
        """Runs pre-flight validation on raw action calls."""
        return self.validator.validate_action(action, parameters)

    async def check_action(self, mission_id: str, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Runs pre-flight validation and risk classification checks."""
        # 1. Block command expansions
        if not self.validate_action(action, parameters):
            self.metrics.record_violation()
            raise PermissionDenied(f"Blocked malicious command expansion pattern in action: {action}")

        # 2. Risk classification
        assessment = self.classify_risk(action, parameters)
        
        # 3. Policy checks
        requires = self.policy.requires_approval(assessment)
        if requires:
            # Check consent
            if self.consent.has_consent(action):
                return {"status": "approved", "risk_level": assessment.risk_level.value, "gated": False}
                
            # Create approval gate
            prompt = self.confirmation.format_prompt(action, parameters, assessment.risk_level)
            app_id = self.manager.create_request(
                mission_id=mission_id,
                action=action,
                risk_level=assessment.risk_level,
                reason=assessment.reason,
                voice_prompt=prompt
            )
            await self.notification.notify_approval_required(app_id, prompt)
            return {"status": "gated", "approval_id": app_id, "risk_level": assessment.risk_level.value, "voice_prompt": prompt}

        return {"status": "approved", "risk_level": assessment.risk_level.value, "gated": False}

    async def approve(self, approval_id: str) -> bool:
        """Resolves request status as approved and writes audit records."""
        start_time = time.time()
        req = self.queue.get_pending(approval_id)
        if not req:
            return False

        res = self.manager.approve(approval_id)
        if res:
            duration = (time.time() - start_time) * 1000.0
            self.metrics.record_response_time(duration)
            self.metrics.record_outcome(True)

            record = AuditRecord(
                record_id=f"rec_{approval_id}",
                mission_id=req.mission_id,
                action=req.action,
                risk_level=req.risk_level,
                approved=True,
                reason="Explicit human approval granted",
                execution_outcome="executed"
            )
            self.audit.log_eval(record)
            await self.event_bridge.publish_audit(record)
            
            # Persist summary inside memory
            summary = f"Human approved action: {req.action} for mission: {req.mission_id} classified as {req.risk_level.value} risk."
            await self.memory.persist_audit(approval_id, summary)

        return res

    async def reject(self, approval_id: str) -> bool:
        """Resolves request status as rejected and writes audit records."""
        start_time = time.time()
        req = self.queue.get_pending(approval_id)
        if not req:
            return False

        res = self.manager.reject(approval_id)
        if res:
            duration = (time.time() - start_time) * 1000.0
            self.metrics.record_response_time(duration)
            self.metrics.record_outcome(False)

            record = AuditRecord(
                record_id=f"rec_{approval_id}",
                mission_id=req.mission_id,
                action=req.action,
                risk_level=req.risk_level,
                approved=False,
                reason="Explicit human approval rejected",
                execution_outcome="blocked"
            )
            self.audit.log_eval(record)
            await self.event_bridge.publish_audit(record)

            summary = f"Human rejected action: {req.action} for mission: {req.mission_id} classified as {req.risk_level.value} risk."
            await self.memory.persist_audit(approval_id, summary)

        return res

    def pending_approvals(self) -> List[ApprovalItem]:
        """Lists pending approvals."""
        return self.queue.list_pending()

    def approval_history(self) -> List[ApprovalItem]:
        """Lists completed histories."""
        return self.queue.list_history()
