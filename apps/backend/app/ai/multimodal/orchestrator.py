"""Central Unified Multimodal Input & Command Orchestration Engine (Phase 10M-A).

Unifies text, voice, vision, and desktop context into a single canonical execution pipeline
powered by LocalModelRouter, CapabilityDiscovery, PlanCritic, TaskGraph, GoalVerifier,
FailureDiagnoser, and DynamicReplanner.
"""

from typing import Any, Dict, List, Optional
import time
import uuid
import structlog

from app.ai.multimodal.models import (
    ActiveAppContext,
    ClarificationOption,
    ClarificationRequest,
    InputModality,
    IntentCategory,
    InteractionState,
    MultimodalConversationContext,
    MultimodalExecutionResult,
    MultimodalTurn,
    NormalizedMultimodalInput,
    ScreenReference,
    StructuredTaskRequest,
)
from app.ai.multimodal.normalizer import MultimodalInputNormalizer
from app.ai.multimodal.intent_analyzer import MultimodalIntentAnalyzer
from app.ai.multimodal.context_manager import MultimodalContextManager
from app.ai.multimodal.voice_interface import MultimodalVoiceInterface
from app.ai.multimodal.vision_grounding import MultimodalVisionGrounder

# Canonical Cognitive Kernel Components
from app.ai.kernel.model_router import LocalModelRouter, CognitiveWorkloadType
from app.ai.kernel.capability_discovery import CapabilityDiscoveryEngine
from app.ai.kernel.kernel_security import KernelSecurityGuard
from app.ai.kernel.plan_critic import PlanCritic, CriticStatus
from app.ai.kernel.task_graph import (
    EdgeCondition,
    NodeState,
    NodeType,
    TaskEdge,
    TaskGraph,
    TaskGraphBuilder,
    TaskGraphExecutor,
    TaskGraphResult,
    TaskGraphStatus,
    TaskNode,
)
from app.ai.kernel.goal_verifier import GoalVerifier, GoalRequirement, VerificationType, VerificationStatus
from app.ai.kernel.failure_diagnoser import FailureDiagnoser
from app.ai.kernel.dynamic_replanner import DynamicReplanner
from app.ai.desktop_automation.models import AutomationAction
from app.ai.desktop_automation.application_adapter import ApplicationAdapterRegistry
from app.ai.desktop_automation.security_engine import SecurityEngine

logger = structlog.get_logger("multimodal_orchestrator")


class UnifiedMultimodalOrchestrator:
    """The central interaction engine connecting text, voice, vision, and autonomous execution."""

    def __init__(
        self,
        normalizer: Optional[MultimodalInputNormalizer] = None,
        intent_analyzer: Optional[MultimodalIntentAnalyzer] = None,
        context_manager: Optional[MultimodalContextManager] = None,
        voice_interface: Optional[MultimodalVoiceInterface] = None,
        vision_grounder: Optional[MultimodalVisionGrounder] = None,
        model_router: Optional[LocalModelRouter] = None,
        capability_engine: Optional[CapabilityDiscoveryEngine] = None,
        security_guard: Optional[KernelSecurityGuard] = None,
        plan_critic: Optional[PlanCritic] = None,
        task_executor: Optional[TaskGraphExecutor] = None,
        goal_verifier: Optional[GoalVerifier] = None,
        failure_diagnoser: Optional[FailureDiagnoser] = None,
        dynamic_replanner: Optional[DynamicReplanner] = None,
    ) -> None:
        # Multimodal Subsystems
        self.context_manager = context_manager or MultimodalContextManager()
        self.voice_interface = voice_interface or MultimodalVoiceInterface()
        self.vision_grounder = vision_grounder or MultimodalVisionGrounder()
        self.normalizer = normalizer or MultimodalInputNormalizer()
        self.intent_analyzer = intent_analyzer or MultimodalIntentAnalyzer(
            vision_grounder=self.vision_grounder
        )

        # Canonical Execution Pipeline Components
        self.model_router = model_router or LocalModelRouter.get_instance()
        self.capability_engine = capability_engine or CapabilityDiscoveryEngine.get_instance()
        self.security_guard = security_guard or KernelSecurityGuard()
        self.plan_critic = plan_critic or PlanCritic(model_router=self.model_router)
        self.task_executor = task_executor or TaskGraphExecutor()
        self.goal_verifier = goal_verifier or GoalVerifier.get_instance()
        self.failure_diagnoser = failure_diagnoser or FailureDiagnoser.get_instance()
        self.dynamic_replanner = dynamic_replanner or DynamicReplanner(
            capability_discovery=self.capability_engine,
            plan_critic=self.plan_critic,
        )

    async def process_text(
        self,
        text: str,
        session_id: Optional[str] = None,
        active_app_override: Optional[str] = None,
    ) -> MultimodalExecutionResult:
        """Convenience method for processing plain text commands."""
        return await self.execute_interaction(
            text=text,
            session_id=session_id,
            active_app_override=active_app_override,
        )

    async def process_voice(
        self,
        audio_bytes: bytes,
        session_id: Optional[str] = None,
        active_app_override: Optional[str] = None,
    ) -> MultimodalExecutionResult:
        """Convenience method for processing spoken voice audio."""
        return await self.execute_interaction(
            audio_bytes=audio_bytes,
            session_id=session_id,
            active_app_override=active_app_override,
        )

    async def process_image(
        self,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        use_screenshot: bool = False,
        prompt: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> MultimodalExecutionResult:
        """Convenience method for visual screen / image analysis."""
        return await self.execute_interaction(
            text=prompt,
            image_path=image_path,
            image_bytes=image_bytes,
            use_screenshot=use_screenshot,
            session_id=session_id,
        )

    async def execute_interaction(
        self,
        text: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        use_screenshot: bool = False,
        session_id: Optional[str] = None,
        active_app_override: Optional[str] = None,
    ) -> MultimodalExecutionResult:
        """Executes the complete unified multimodal interaction and task lifecycle."""
        start_time = time.time()
        sid = session_id or f"session_{uuid.uuid4().hex[:8]}"

        # 1. Check for Active Cancellation
        if self.voice_interface.is_interrupted(sid):
            self.context_manager.set_state(sid, InteractionState.CANCELLED)
            return self._build_result(
                session_id=sid,
                state=InteractionState.CANCELLED,
                success=True,
                spoken_response="Operation was cancelled.",
                structured_request=StructuredTaskRequest(
                    intent_category=IntentCategory.CANCEL_ACTION,
                    primary_goal="Cancel operation",
                    action_type="cancel",
                ),
                start_time=start_time,
            )

        # 2. Input Normalization
        self.context_manager.set_state(sid, InteractionState.PROCESSING)
        self.voice_interface.set_state(sid, InteractionState.PROCESSING)

        normalized_input = await self.normalizer.normalize(
            text=text,
            audio_bytes=audio_bytes,
            image_path=image_path,
            image_bytes=image_bytes,
            use_screenshot=use_screenshot,
            session_id=sid,
            active_app_override=active_app_override,
        )

        # 3. Context Retrieval & State Tracking
        context = self.context_manager.get_or_create_context(sid)

        # 4. Semantic Intent Understanding & Visual Grounding
        task_request = await self.intent_analyzer.analyze_intent(normalized_input, context)
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        self.context_manager.set_active_task(sid, task_id, task_request.target_app)

        # 5. Handle Cancellation Request
        if task_request.intent_category == IntentCategory.CANCEL_ACTION:
            self.context_manager.set_state(sid, InteractionState.CANCELLED)
            self.voice_interface.set_state(sid, InteractionState.CANCELLED)
            self.context_manager.clear_pending_clarification(sid)
            return self._build_result(
                session_id=sid,
                task_id=task_id,
                state=InteractionState.CANCELLED,
                success=True,
                spoken_response="Operation cancelled as requested.",
                structured_request=task_request,
                start_time=start_time,
            )

        # 6. Handle Missing Information / Required Clarification
        if task_request.needs_clarification and task_request.clarification_request:
            clar = task_request.clarification_request
            self.context_manager.set_pending_clarification(sid, clar)
            self.voice_interface.set_state(sid, InteractionState.AWAITING_CLARIFICATION)

            spoken_msg = clar.prompt
            tts_path = None
            if normalized_input.modality in [InputModality.VOICE, InputModality.MIXED]:
                tts_path = await self._synthesize_voice_safe(spoken_msg, sid)

            self.context_manager.record_turn(
                session_id=sid,
                user_text=normalized_input.effective_text,
                modality=normalized_input.modality,
                status="awaiting_clarification",
                task_request=task_request,
                agent_response_text=spoken_msg,
                tts_audio_path=tts_path,
            )

            return self._build_result(
                session_id=sid,
                task_id=task_id,
                state=InteractionState.AWAITING_CLARIFICATION,
                success=False,
                spoken_response=spoken_msg,
                tts_audio_path=tts_path,
                structured_request=task_request,
                clarification=clar,
                visual_uncertainty=task_request.visual_uncertainty,
                start_time=start_time,
            )

        # 7. Safety Policy Check: Visual Uncertainty Gating
        if task_request.visual_uncertainty:
            self.context_manager.set_state(sid, InteractionState.AWAITING_CLARIFICATION)
            warning_msg = (
                f"Action halted: Screen target is uncertain ({task_request.uncertainty_reason or 'ambiguous element'}). "
                "Nova policy forbids executing actions on uncertain visual interpretation."
            )
            return self._build_result(
                session_id=sid,
                task_id=task_id,
                state=InteractionState.AWAITING_CLARIFICATION,
                success=False,
                spoken_response=warning_msg,
                structured_request=task_request,
                visual_uncertainty=True,
                start_time=start_time,
            )

        # 8. Security Policy Check: Human Approval Gating
        if task_request.requires_user_approval:
            self.context_manager.set_state(sid, InteractionState.AWAITING_CLARIFICATION)
            approval_msg = (
                f"Action '{task_request.action_type}' in {task_request.target_app} requires explicit user approval "
                "due to high security sensitivity."
            )
            return self._build_result(
                session_id=sid,
                task_id=task_id,
                state=InteractionState.AWAITING_CLARIFICATION,
                success=False,
                spoken_response=approval_msg,
                structured_request=task_request,
                approval_required=True,
                start_time=start_time,
            )

        # Clear any prior pending clarification since we are proceeding to execution
        self.context_manager.clear_pending_clarification(sid)

        # 9. Handle Pure Conversation
        if task_request.intent_category == IntentCategory.CONVERSATION:
            resp_text = f"I understand: {task_request.primary_goal}. How can I assist you with your desktop tasks?"
            tts_path = None
            if normalized_input.modality in [InputModality.VOICE, InputModality.MIXED]:
                tts_path = await self._synthesize_voice_safe(resp_text, sid)

            self.context_manager.record_turn(
                session_id=sid,
                user_text=normalized_input.effective_text,
                modality=normalized_input.modality,
                status="completed",
                task_request=task_request,
                agent_response_text=resp_text,
                tts_audio_path=tts_path,
            )

            return self._build_result(
                session_id=sid,
                task_id=task_id,
                state=InteractionState.COMPLETED,
                success=True,
                spoken_response=resp_text,
                tts_audio_path=tts_path,
                structured_request=task_request,
                start_time=start_time,
            )

        # 10. Canonical Execution Pipeline: TaskGraph Construction & Planning
        self.context_manager.set_state(sid, InteractionState.PLANNING)
        self.voice_interface.set_state(sid, InteractionState.PLANNING)

        graph = self._build_task_graph(task_id, task_request)

        # 11. PlanCritic Pre-Execution Evaluation
        critic_res = self.plan_critic.evaluate_plan(
            user_goal=task_request.primary_goal,
            plan_nodes=[n.to_dict() for n in graph.nodes.values()],
            use_semantic_critic=False,
        )
        critic_data = {
            "status": critic_res.status.value,
            "approved": critic_res.status == CriticStatus.APPROVED,
            "confidence": critic_res.confidence,
            "issues": [i.to_dict() for i in critic_res.issues],
        }

        # 12. Canonical Task Execution via TaskGraphExecutor
        self.context_manager.set_state(sid, InteractionState.EXECUTING)
        self.voice_interface.set_state(sid, InteractionState.EXECUTING)

        exec_res: TaskGraphResult = await self.task_executor.execute(
            graph=graph,
            user_goal=task_request.primary_goal,
        )

        # 13. Goal Verification via GoalVerifier
        self.context_manager.set_state(sid, InteractionState.VERIFYING)
        self.voice_interface.set_state(sid, InteractionState.VERIFYING)

        goal_requirements = [
            GoalRequirement(
                requirement_id=f"req_{task_request.action_type}",
                description=f"Execute {task_request.action_type} for {task_request.target_app}",
                verification_type=VerificationType.STATE,
                target_entity=task_request.target_app,
                expected_value="SUCCESS",
            )
        ]

        action_results = [
            n.result.to_dict() if hasattr(n.result, "to_dict") else {"node_id": n.node_id, "success": True}
            for n in graph.nodes.values()
            if n.result is not None
        ]

        verification_result = self.goal_verifier.verify_goal(
            user_goal=task_request.primary_goal,
            requirements=goal_requirements,
            adapter_name=task_request.target_app if task_request.target_app != "System" else None,
            execution_summary={
                "task_id": task_id,
                "status": "SUCCESS" if exec_res.status == TaskGraphStatus.SUCCESS else "FAILED",
                "action_results": action_results,
            },
        )
        verif_data = verification_result.to_dict()

        # 14. Failure Diagnosis & Dynamic Replanning (if needed)
        replan_data = None
        is_success = exec_res.status == TaskGraphStatus.SUCCESS and verification_result.goal_satisfied

        if not is_success and exec_res.status != TaskGraphStatus.CANCELLED:
            logger.info("Task execution not fully satisfied, diagnosing failure", task_id=task_id)
            diag = self.failure_diagnoser.diagnose_failure(
                task_id=task_id,
                user_goal=task_request.primary_goal,
                action_result={"error": exec_res.error_message or "Goal verification condition not fully satisfied"},
            )
            # Attempt Dynamic Replanning
            replan_res = self.dynamic_replanner.replan(
                task_id=task_id,
                user_goal=task_request.primary_goal,
                current_graph=graph,
                diagnosis=diag,
            )
            replan_data = replan_res.to_dict()

        # 15. Formulate Spoken & Text Response
        if is_success:
            spoken_text = f"Successfully executed {task_request.action_type} in {task_request.target_app}. Goal verified."
        else:
            spoken_text = f"Execution for '{task_request.primary_goal}' completed with status {exec_res.status.value}."

        tts_path = None
        if normalized_input.modality in [InputModality.VOICE, InputModality.MIXED]:
            tts_path = await self._synthesize_voice_safe(spoken_text, sid)

        final_state = InteractionState.COMPLETED if is_success else InteractionState.FAILED
        self.context_manager.set_state(sid, final_state)
        self.voice_interface.set_state(sid, final_state)

        # Record interaction turn in context
        self.context_manager.record_turn(
            session_id=sid,
            user_text=normalized_input.effective_text,
            modality=normalized_input.modality,
            status="completed" if is_success else "failed",
            task_request=task_request,
            agent_response_text=spoken_text,
            tts_audio_path=tts_path,
        )

        task_graph_dict = {
            "graph_id": exec_res.graph_id,
            "task_id": exec_res.task_id,
            "status": exec_res.status.value,
            "executed_nodes_count": exec_res.executed_nodes_count,
            "succeeded_nodes_count": exec_res.succeeded_nodes_count,
            "failed_nodes_count": exec_res.failed_nodes_count,
            "blocked_nodes_count": exec_res.blocked_nodes_count,
            "skipped_nodes_count": exec_res.skipped_nodes_count,
            "duration_sec": exec_res.duration_sec,
        }

        return self._build_result(
            session_id=sid,
            task_id=task_id,
            state=final_state,
            success=is_success,
            spoken_response=spoken_text,
            tts_audio_path=tts_path,
            structured_request=task_request,
            task_graph_result=task_graph_dict,
            goal_verification=verif_data,
            critic_result=critic_data,
            start_time=start_time,
        )

    def _build_task_graph(self, task_id: str, req: StructuredTaskRequest) -> TaskGraph:
        """Constructs an executable stateful DAG TaskGraph for target request."""
        # Action Node
        action_payload = AutomationAction(
            action_type=req.action_type,
            target_application=req.target_app,
            parameters=req.parameters,
        )
        action_node = TaskNode(
            node_id=f"node_act_{uuid.uuid4().hex[:6]}",
            title=f"Execute {req.action_type}",
            node_type=NodeType.ACTION,
            action=action_payload,
            metadata={"target_app": req.target_app},
        )

        # Verification Node
        verify_node = TaskNode(
            node_id=f"node_ver_{uuid.uuid4().hex[:6]}",
            title=f"Verify {req.primary_goal}",
            node_type=NodeType.VERIFY,
            metadata={"user_goal": req.primary_goal},
        )

        edge = TaskEdge(
            edge_id=f"edge_{uuid.uuid4().hex[:6]}",
            source_node_id=action_node.node_id,
            target_node_id=verify_node.node_id,
            condition=EdgeCondition.ON_SUCCESS,
        )

        graph = TaskGraph(
            graph_id=f"graph_{uuid.uuid4().hex[:8]}",
            task_id=task_id,
        )
        graph.add_node(action_node)
        graph.add_node(verify_node)
        graph.add_edge(edge)
        return graph

    async def _synthesize_voice_safe(self, text: str, session_id: str) -> Optional[str]:
        """Safely synthesizes TTS voice response with local engine and error suppression."""
        try:
            return await self.voice_interface.speak(text, session_id)
        except Exception as e:
            logger.warning("TTS generation encountered non-fatal error", error=str(e))
            return None

    def _build_result(
        self,
        session_id: str,
        state: InteractionState,
        success: bool,
        spoken_response: str,
        structured_request: StructuredTaskRequest,
        task_id: Optional[str] = None,
        tts_audio_path: Optional[str] = None,
        task_graph_result: Optional[Dict[str, Any]] = None,
        goal_verification: Optional[Dict[str, Any]] = None,
        critic_result: Optional[Dict[str, Any]] = None,
        approval_required: bool = False,
        visual_uncertainty: bool = False,
        clarification: Optional[ClarificationRequest] = None,
        error: Optional[str] = None,
        start_time: float = 0.0,
    ) -> MultimodalExecutionResult:
        """Helper to construct strongly typed MultimodalExecutionResult."""
        elapsed_ms = (time.time() - start_time) * 1000.0 if start_time > 0 else 0.0
        return MultimodalExecutionResult(
            session_id=session_id,
            task_id=task_id or f"task_{uuid.uuid4().hex[:8]}",
            state=state,
            success=success,
            spoken_response=spoken_response,
            tts_audio_path=tts_audio_path,
            structured_request=structured_request,
            task_graph_result=task_graph_result,
            goal_verification=goal_verification,
            critic_result=critic_result,
            approval_required=approval_required,
            visual_uncertainty=visual_uncertainty,
            clarification=clarification,
            error=error,
            latency_ms=elapsed_ms,
        )
