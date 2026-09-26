"""Native Failure Diagnoser for Nova-AI's Cognitive Kernel.

Consumes execution evidence, observations, and GoalVerifier replan contexts to produce
structured failure diagnoses classifying root cause, confidence, recoverability, and recommended recovery.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import asyncio
import json
import structlog

from app.ai.kernel.model_router import CognitiveWorkloadType, LocalModelRouter
from app.ai.runtime.llm_runtime import LLMRuntime

from app.ai.runtime.models import RuntimeRequest

logger = structlog.get_logger("failure_diagnoser")


class FailureType(str, Enum):
    """Categorized failure types for cognitive workflow execution."""

    ACTION_FAILURE = "ACTION_FAILURE"
    PRECONDITION_FAILURE = "PRECONDITION_FAILURE"
    POSTCONDITION_FAILURE = "POSTCONDITION_FAILURE"
    GOAL_VERIFICATION_FAILURE = "GOAL_VERIFICATION_FAILURE"
    CAPABILITY_MISMATCH = "CAPABILITY_MISMATCH"
    STATE_CHANGED = "STATE_CHANGED"
    RESOURCE_FAILURE = "RESOURCE_FAILURE"
    TIMEOUT = "TIMEOUT"
    SECURITY_BLOCK = "SECURITY_BLOCK"
    UNKNOWN_UNVERIFIED = "UNKNOWN_UNVERIFIED"


class Recoverability(str, Enum):
    """Recoverability classification for diagnosed failures."""

    RECOVERABLE = "RECOVERABLE"
    RETRYABLE = "RETRYABLE"
    NON_RECOVERABLE = "NON_RECOVERABLE"
    HUMAN_REQUIRED = "HUMAN_REQUIRED"


class ExecutionControlState(str, Enum):
    """Control states for execution engine lifecycle."""

    CONTINUE = "CONTINUE"
    RETRY = "RETRY"
    REPLAN = "REPLAN"
    BLOCKED = "BLOCKED"
    REQUIRES_HUMAN = "REQUIRES_HUMAN"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


@dataclass
class FailureDiagnosis:
    """Structured failure diagnosis output."""

    failure_type: FailureType
    root_cause: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    affected_requirement: Optional[str] = None
    affected_node: Optional[str] = None
    confidence: float = 1.0
    recoverability: Recoverability = Recoverability.RECOVERABLE
    recommended_recovery: ExecutionControlState = ExecutionControlState.REPLAN
    requires_human: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Converts diagnosis to dictionary representation."""
        return {
            "failure_type": self.failure_type.value,
            "root_cause": self.root_cause,
            "evidence": self.evidence,
            "affected_requirement": self.affected_requirement,
            "affected_node": self.affected_node,
            "confidence": self.confidence,
            "recoverability": self.recoverability.value,
            "recommended_recovery": self.recommended_recovery.value,
            "requires_human": self.requires_human,
        }


class FailureDiagnoser:
    """Deterministic structural and semantic failure diagnoser."""

    _instance: Optional["FailureDiagnoser"] = None

    @classmethod
    def get_instance(cls) -> "FailureDiagnoser":
        """Singleton accessor."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def diagnose_failure(
        self,
        task_id: str,
        user_goal: str,
        node_id: Optional[str] = None,
        action_result: Optional[Dict[str, Any]] = None,
        goal_verification_details: Optional[Dict[str, Any]] = None,
        world_state_data: Optional[Dict[str, Any]] = None,
        working_memory_task: Optional[Any] = None,
        allow_model_fallback: bool = True,
    ) -> FailureDiagnosis:
        """Diagnoses workflow failure using deterministic rules first, then semantic LLM reasoning if necessary."""
        action_result = action_result or {}
        goal_details = goal_verification_details or {}
        error_msg = str(action_result.get("error_message") or action_result.get("error") or action_result.get("message") or action_result.get("reason") or "").lower()
        stdout = str(action_result.get("stdout") or "").lower()
        stderr = str(action_result.get("stderr") or "").lower()
        combined_err = f"{error_msg} {stdout} {stderr}".strip()

        # Check working memory retries
        retries_used = working_memory_task.retries_used if working_memory_task else 0
        max_retries = working_memory_task.max_retries if working_memory_task else 3

        # 1. SECURITY_BLOCK Rule
        if any(kw in combined_err for kw in ["security", "permission", "approval", "unauthorized", "access denied", "security_block"]):
            return FailureDiagnosis(
                failure_type=FailureType.SECURITY_BLOCK,
                root_cause=f"Security engine blocked execution on node '{node_id}': {action_result.get('error', 'Approval required')}",
                evidence={"action_result": action_result, "error": combined_err},
                affected_node=node_id,
                confidence=1.0,
                recoverability=Recoverability.HUMAN_REQUIRED,
                recommended_recovery=ExecutionControlState.REQUIRES_HUMAN,
                requires_human=True,
            )

        # 2. TIMEOUT Rule
        if any(kw in combined_err for kw in ["timeout", "timed out", "wait threshold", "deadline exceeded"]):
            can_retry = retries_used < max_retries
            return FailureDiagnosis(
                failure_type=FailureType.TIMEOUT,
                root_cause=f"Execution timed out on node '{node_id}': {action_result.get('error', 'Timeout reached')}",
                evidence={"action_result": action_result, "retries_used": retries_used},
                affected_node=node_id,
                confidence=1.0,
                recoverability=Recoverability.RETRYABLE if can_retry else Recoverability.RECOVERABLE,
                recommended_recovery=ExecutionControlState.RETRY if can_retry else ExecutionControlState.REPLAN,
                requires_human=False,
            )

        # 3. CAPABILITY_MISMATCH Rule
        if any(kw in combined_err for kw in ["not supported", "capability not found", "invalid capability", "no adapter", "unknown action", "missing capability", "mock error", "invalid action"]):
            return FailureDiagnosis(
                failure_type=FailureType.CAPABILITY_MISMATCH,
                root_cause=f"Capability mismatch on node '{node_id}': capability is invalid or unsupported in current environment",
                evidence={"action_result": action_result},
                affected_node=node_id,
                confidence=1.0,
                recoverability=Recoverability.RECOVERABLE,
                recommended_recovery=ExecutionControlState.REPLAN,
                requires_human=False,
            )

        # 4. PRECONDITION_FAILURE Rule
        if any(kw in combined_err for kw in ["precondition", "prerequisite", "missing input", "input file missing", "not found in scene", "does not exist"]):
            return FailureDiagnosis(
                failure_type=FailureType.PRECONDITION_FAILURE,
                root_cause=f"Precondition failed for node '{node_id}': required input state or asset is missing",
                evidence={"action_result": action_result, "world_state": world_state_data},
                affected_node=node_id,
                confidence=0.95,
                recoverability=Recoverability.RECOVERABLE,
                recommended_recovery=ExecutionControlState.REPLAN,
                requires_human=False,
            )

        # 5. STATE_CHANGED Rule
        if any(kw in combined_err for kw in ["state changed", "scene modified", "external mutation", "unexpected active object", "modified externally"]):
            return FailureDiagnosis(
                failure_type=FailureType.STATE_CHANGED,
                root_cause=f"Environment state changed unexpectedly prior to/during node '{node_id}' execution",
                evidence={"action_result": action_result, "world_state": world_state_data},
                affected_node=node_id,
                confidence=0.95,
                recoverability=Recoverability.RECOVERABLE,
                recommended_recovery=ExecutionControlState.REPLAN,
                requires_human=False,
            )

        # 6. RESOURCE_FAILURE Rule
        if any(kw in combined_err for kw in ["out of memory", "disk full", "connection refused", "resource exhausted", "no space"]):
            return FailureDiagnosis(
                failure_type=FailureType.RESOURCE_FAILURE,
                root_cause=f"Resource failure on node '{node_id}': system hardware/network constraint encountered",
                evidence={"action_result": action_result},
                affected_node=node_id,
                confidence=0.95,
                recoverability=Recoverability.RECOVERABLE,
                recommended_recovery=ExecutionControlState.REPLAN,
                requires_human=False,
            )

        # 7. POSTCONDITION_FAILURE Rule
        if action_result.get("postcondition_failed") or action_result.get("status") == "POSTCONDITION_FAILED":
            return FailureDiagnosis(
                failure_type=FailureType.POSTCONDITION_FAILURE,
                root_cause=f"Postcondition assertion failed for node '{node_id}': output artifact or state verification missing",
                evidence={"action_result": action_result},
                affected_node=node_id,
                confidence=1.0,
                recoverability=Recoverability.RECOVERABLE,
                recommended_recovery=ExecutionControlState.REPLAN,
                requires_human=False,
            )

        # 8. GOAL_VERIFICATION_FAILURE Rule
        if goal_details.get("status") == "FAILED" or goal_details.get("failed_requirement_ids"):
            failed_reqs = goal_details.get("failed_requirement_ids", [])
            affected_req = failed_reqs[0] if failed_reqs else None
            return FailureDiagnosis(
                failure_type=FailureType.GOAL_VERIFICATION_FAILURE,
                root_cause=f"Goal verification failed: unsatisfied requirement(s) {failed_reqs}",
                evidence={"goal_verification_details": goal_details},
                affected_requirement=affected_req,
                affected_node=node_id,
                confidence=1.0,
                recoverability=Recoverability.RECOVERABLE,
                recommended_recovery=ExecutionControlState.REPLAN,
                requires_human=False,
            )

        # 9. ACTION_FAILURE Rule
        err_str = str(action_result.get("error") or action_result.get("error_message") or "").lower()
        if (action_result.get("status") in ["FAILED", "ERROR"] or action_result.get("success") is False or err_str) and "opaque" not in err_str:
            transient = action_result.get("transient", True)
            can_retry = transient and (retries_used < max_retries)
            return FailureDiagnosis(
                failure_type=FailureType.ACTION_FAILURE,
                root_cause=f"Action execution error on node '{node_id}': {action_result.get('error', combined_err or 'Action failed')}",
                evidence={"action_result": action_result, "retries_used": retries_used},
                affected_node=node_id,
                confidence=0.9,
                recoverability=Recoverability.RETRYABLE if can_retry else Recoverability.RECOVERABLE,
                recommended_recovery=ExecutionControlState.RETRY if can_retry else ExecutionControlState.REPLAN,
                requires_human=False,
            )

        # 10. Unknown / Semantic LLM fallback
        if allow_model_fallback:
            semantic_diag = self._semantic_diagnosis_fallback(
                task_id=task_id,
                user_goal=user_goal,
                node_id=node_id,
                action_result=action_result,
                goal_verification_details=goal_details,
            )
            if semantic_diag:
                return semantic_diag

        # Default fallback: UNKNOWN_UNVERIFIED
        return FailureDiagnosis(
            failure_type=FailureType.UNKNOWN_UNVERIFIED,
            root_cause=f"Unverified failure on node '{node_id}': no deterministic rule or verified diagnosis matched",
            evidence={"action_result": action_result, "goal_verification_details": goal_details},
            affected_node=node_id,
            confidence=0.3,
            recoverability=Recoverability.NON_RECOVERABLE,
            recommended_recovery=ExecutionControlState.FAILED,
            requires_human=True,
        )

    def _semantic_diagnosis_fallback(
        self,
        task_id: str,
        user_goal: str,
        node_id: Optional[str],
        action_result: Dict[str, Any],
        goal_verification_details: Dict[str, Any],
    ) -> Optional[FailureDiagnosis]:
        """Uses LocalModelRouter reasoning workload to classify opaque failures."""
        try:
            router = LocalModelRouter.get_instance()
            decision = router.route(CognitiveWorkloadType.REASONING)
            prompt = (
                f"Analyze the following workflow execution failure and return JSON with keys:\n"
                f"- failure_type: one of [ACTION_FAILURE, PRECONDITION_FAILURE, POSTCONDITION_FAILURE, GOAL_VERIFICATION_FAILURE, CAPABILITY_MISMATCH, STATE_CHANGED, RESOURCE_FAILURE, TIMEOUT, SECURITY_BLOCK, UNKNOWN_UNVERIFIED]\n"
                f"- root_cause: string explanation\n"
                f"- confidence: float between 0 and 1\n"
                f"- recoverability: one of [RECOVERABLE, RETRYABLE, NON_RECOVERABLE, HUMAN_REQUIRED]\n"
                f"- recommended_recovery: one of [RETRY, REPLAN, REQUIRES_HUMAN, FAILED]\n"
                f"- requires_human: boolean\n\n"
                f"User Goal: {user_goal}\n"
                f"Node ID: {node_id}\n"
                f"Action Result: {json.dumps(action_result)}\n"
                f"Goal Verification Details: {json.dumps(goal_verification_details)}\n"
            )

            async def _run_llm():
                llm = LLMRuntime.get_instance()
                req = RuntimeRequest(prompt=prompt, model_id=decision.selected_model_id)
                return await llm.generate(req)

            try:
                loop = asyncio.get_running_loop()
                response = asyncio.run_coroutine_threadsafe(_run_llm(), loop).result(timeout=10.0)
            except RuntimeError:
                response = asyncio.run(_run_llm())

            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            parsed = json.loads(content)
            ftype_str = parsed.get("failure_type", "UNKNOWN_UNVERIFIED")
            rec_str = parsed.get("recoverability", "NON_RECOVERABLE")
            recovery_str = parsed.get("recommended_recovery", "FAILED")

            return FailureDiagnosis(
                failure_type=FailureType(ftype_str) if ftype_str in FailureType.__members__ else FailureType.UNKNOWN_UNVERIFIED,
                root_cause=parsed.get("root_cause", "Semantic analysis diagnosed failure"),
                evidence={"semantic_response": parsed, "action_result": action_result},
                affected_node=node_id,
                confidence=float(parsed.get("confidence", 0.7)),
                recoverability=Recoverability(rec_str) if rec_str in Recoverability.__members__ else Recoverability.NON_RECOVERABLE,
                recommended_recovery=ExecutionControlState(recovery_str) if recovery_str in ExecutionControlState.__members__ else ExecutionControlState.FAILED,
                requires_human=bool(parsed.get("requires_human", False)),
            )
        except Exception as e:
            logger.warning("Semantic failure diagnosis fallback failed", error=str(e))
            return None
