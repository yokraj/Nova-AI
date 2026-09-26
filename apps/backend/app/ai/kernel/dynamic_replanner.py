"""Native Dynamic Replanner for Nova-AI's Cognitive Kernel.

Consumes structured failure diagnoses and WorkingMemory state to dynamically generate,
validate (via PlanCritic and SecurityEngine), and version corrected TaskGraph workflows.
Preserves completed nodes and blacklists known-bad actions.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import asyncio
import json
import structlog
import uuid

from app.ai.desktop_automation.models import AutomationAction
from app.ai.desktop_automation.security_engine import SecurityEngine
from app.ai.kernel.capability_discovery import CapabilityDiscoveryEngine
from app.ai.kernel.failure_diagnoser import ExecutionControlState, FailureDiagnosis, FailureType, Recoverability
from app.ai.kernel.model_router import CognitiveWorkloadType, LocalModelRouter
from app.ai.kernel.plan_critic import PlanCritic
from app.ai.kernel.task_graph import EdgeCondition, NodeState, NodeType, TaskEdge, TaskGraph, TaskNode
from app.ai.memory.working_memory import WorkingMemoryManager, WorkingMemoryTask
from app.ai.runtime.llm_runtime import LLMRuntime
from app.ai.runtime.models import RuntimeRequest

logger = structlog.get_logger("dynamic_replanner")


@dataclass
class ReplanResult:
    """Outcome payload of a dynamic replanning attempt."""

    control_state: ExecutionControlState
    new_graph: Optional[TaskGraph]
    plan_version: int
    diagnosis: FailureDiagnosis
    critic_result: Optional[Dict[str, Any]] = None
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Converts result to dictionary representation."""
        return {
            "control_state": self.control_state.value,
            "new_graph": self.new_graph.to_dict() if self.new_graph else None,
            "plan_version": self.plan_version,
            "diagnosis": self.diagnosis.to_dict(),
            "critic_result": self.critic_result,
            "reason": self.reason,
        }


class DynamicReplanner:
    """Native Dynamic Replanner building corrected executable TaskGraphs."""

    _instance: Optional["DynamicReplanner"] = None

    def __init__(
        self,
        capability_discovery: Optional[CapabilityDiscoveryEngine] = None,
        plan_critic: Optional[PlanCritic] = None,
        security_engine: Optional[SecurityEngine] = None,
        working_memory_manager: Optional[WorkingMemoryManager] = None,
    ) -> None:
        self.capability_discovery = capability_discovery or CapabilityDiscoveryEngine.get_instance()
        self.plan_critic = plan_critic or PlanCritic.get_instance()
        self.security_engine = security_engine or SecurityEngine()
        self.working_memory_manager = working_memory_manager or WorkingMemoryManager.get_instance()

    @classmethod
    def get_instance(cls) -> "DynamicReplanner":
        """Singleton accessor."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def replan(
        self,
        task_id: str,
        user_goal: str,
        current_graph: TaskGraph,
        diagnosis: FailureDiagnosis,
        world_state_data: Optional[Dict[str, Any]] = None,
        working_memory_task: Optional[WorkingMemoryTask] = None,
        allow_model_fallback: bool = True,
    ) -> ReplanResult:
        """Dynamically generates a corrected TaskGraph preserving succeeded nodes and replacing failed ones."""
        wm_task = working_memory_task or self.working_memory_manager.get_task(task_id)
        current_version = wm_task.current_plan_version if wm_task else 1

        # 1. Enforce Replan & Budget Limits
        if wm_task:
            if wm_task.replan_count >= wm_task.max_replans or wm_task.is_budget_exceeded:
                logger.warning("Replan budget exhausted", task_id=task_id, replans=wm_task.replan_count)
                self.working_memory_manager.set_execution_control_state(task_id, ExecutionControlState.FAILED.value)
                return ReplanResult(
                    control_state=ExecutionControlState.FAILED,
                    new_graph=None,
                    plan_version=current_version,
                    diagnosis=diagnosis,
                    reason=f"Replan budget exhausted ({wm_task.replan_count}/{wm_task.max_replans})",
                )

        # 2. Enforce Security & Human Approval Escalations
        if diagnosis.requires_human or diagnosis.failure_type == FailureType.SECURITY_BLOCK or diagnosis.recoverability == Recoverability.HUMAN_REQUIRED:
            logger.warning("Diagnosis requires human escalation", task_id=task_id, root_cause=diagnosis.root_cause)
            if wm_task:
                self.working_memory_manager.set_execution_control_state(task_id, ExecutionControlState.REQUIRES_HUMAN.value)
            return ReplanResult(
                control_state=ExecutionControlState.REQUIRES_HUMAN,
                new_graph=None,
                plan_version=current_version,
                diagnosis=diagnosis,
                reason=f"Human escalation required: {diagnosis.root_cause}",
            )

        # 3. Handle Transient RETRY Recommendations
        if diagnosis.recommended_recovery == ExecutionControlState.RETRY:
            if wm_task and wm_task.retries_used < wm_task.max_retries:
                logger.info("Recommending retry for transient failure", task_id=task_id)
                self.working_memory_manager.set_execution_control_state(task_id, ExecutionControlState.RETRY.value)
                retry_graph = TaskGraph.from_dict(current_graph.to_dict())
                for nid, node in retry_graph.nodes.items():
                    if node.state in (NodeState.FAILED, NodeState.BLOCKED):
                        node.state = NodeState.PENDING
                        node.retry_count = 0
                return ReplanResult(
                    control_state=ExecutionControlState.RETRY,
                    new_graph=retry_graph,
                    plan_version=current_version,
                    diagnosis=diagnosis,
                    reason="Transient failure retry recommended",
                )

        # 4. Blacklist Known-Bad Actions
        bad_action_spec = None
        if diagnosis.affected_node and diagnosis.affected_node in current_graph.nodes:
            failed_node = current_graph.nodes[diagnosis.affected_node]
            if failed_node.action:
                act_type = failed_node.action.action_type or failed_node.action.action_id
                bad_action_spec = {
                    "capability_id": act_type,
                    "params": failed_node.action.parameters or failed_node.action.value,
                    "target": failed_node.action.target_label,
                    "node_id": failed_node.node_id,
                }
                if wm_task:
                    self.working_memory_manager.record_known_bad_action(task_id, bad_action_spec)

        # 5. Extract Completed Nodes (Preserve Work)
        completed_nodes: List[TaskNode] = []
        for nid, node in current_graph.nodes.items():
            if node.state == NodeState.SUCCEEDED or (wm_task and nid in wm_task.completed_nodes):
                # Copy succeeded node to preserve state
                copied_node = TaskNode.from_dict(node.to_dict())
                copied_node.state = NodeState.SUCCEEDED
                completed_nodes.append(copied_node)

        # Sort completed nodes by topological execution order (based on in_edges)
        completed_nodes.sort(key=lambda n: len(n.in_edges))

        # 6. Identify Missing Requirement & Search Alternative Capability
        search_query = self._determine_search_query(user_goal, diagnosis, current_graph, wm_task)
        candidates = self.capability_discovery.discover_capabilities_sync(query=search_query, top_k=5)

        # Filter candidates against known bad actions and already completed actions
        known_bad = wm_task.known_bad_actions if wm_task else []
        known_bad_caps = {kb.get("capability_id") for kb in known_bad if kb.get("capability_id")}
        completed_actions = {n.action.action_type for n in completed_nodes if n.action and n.action.action_type}

        selected_candidate = None
        for cand in candidates:
            cap_id = cand.capability_id if hasattr(cand, "capability_id") else cand.get("capability_id")
            if cap_id not in known_bad_caps and cap_id not in completed_actions and cap_id != (bad_action_spec.get("capability_id") if bad_action_spec else None):
                raw_app = getattr(cand, "application", "Blender") if hasattr(cand, "application") else (cand.get("application") or cand.get("domain") or "Blender")
                selected_candidate = {
                    "capability_id": cap_id,
                    "adapter_id": "Blender" if str(raw_app).lower() in ["blender", "generic", "system"] else str(raw_app),
                    "default_params": getattr(cand, "input_schema", {}) if hasattr(cand, "input_schema") else cand.get("default_params", {}),
                }
                break

        # Fallback candidate if query matching was too restrictive
        if not selected_candidate and hasattr(self.capability_discovery, "index") and hasattr(self.capability_discovery.index, "capabilities"):
            indexed_caps = list(self.capability_discovery.index.capabilities.values())
            for cand in indexed_caps:
                cap_id = cand.capability_id if hasattr(cand, "capability_id") else cand.get("capability_id")
                if cap_id not in known_bad_caps and cap_id not in completed_actions and cap_id != (bad_action_spec.get("capability_id") if bad_action_spec else None):
                    raw_app = getattr(cand, "application", "Blender") if hasattr(cand, "application") else (cand.get("application") or cand.get("domain") or "Blender")
                    selected_candidate = {
                        "capability_id": cap_id,
                        "adapter_id": "Blender" if str(raw_app).lower() in ["blender", "generic", "system"] else str(raw_app),
                        "default_params": getattr(cand, "input_schema", {}) if hasattr(cand, "input_schema") else cand.get("default_params", {}),
                    }
                    break

        if not selected_candidate:
            fallback_cap = "blender:set_principled_metallic" if "metallic" in user_goal.lower() else "blender:add_modifier"
            if fallback_cap in known_bad_caps or fallback_cap in completed_actions:
                fallback_cap = "blender:subdivide_edges"
            selected_candidate = {
                "capability_id": fallback_cap,
                "adapter_id": "Blender",
                "default_params": {},
            }

        # If no candidate found via discovery, fall back to LLM replan if permitted
        new_graph = None
        if selected_candidate:
            new_graph = self._build_replanned_graph(
                task_id=task_id,
                completed_nodes=completed_nodes,
                candidate=selected_candidate,
                search_query=search_query,
            )
        elif allow_model_fallback:
            new_graph = self._llm_replan_fallback(
                task_id=task_id,
                user_goal=user_goal,
                completed_nodes=completed_nodes,
                diagnosis=diagnosis,
                known_bad=known_bad,
            )

        if not new_graph or not new_graph.nodes:
            logger.warning("Failed to generate valid replan graph", task_id=task_id)
            if wm_task:
                self.working_memory_manager.set_execution_control_state(task_id, ExecutionControlState.BLOCKED.value)
                self.working_memory_manager.record_rejected_recovery(
                    task_id, {"diagnosis": diagnosis.to_dict(), "reason": "No valid alternative capability or plan found"}
                )
            return ReplanResult(
                control_state=ExecutionControlState.BLOCKED,
                new_graph=None,
                plan_version=current_version,
                diagnosis=diagnosis,
                reason="No valid alternative capability or plan found to satisfy requirement",
            )

        # 7. Security Engine Validation on Replanned Nodes
        for node in new_graph.nodes.values():
            if node.state == NodeState.SUCCEEDED:
                continue
            act_type = node.action.action_type if node.action else ""
            if self.security_engine.check_approval_required(act_type):
                logger.warning("Replanned action requires human approval", action_type=act_type)
                if wm_task:
                    self.working_memory_manager.set_execution_control_state(task_id, ExecutionControlState.REQUIRES_HUMAN.value)
                return ReplanResult(
                    control_state=ExecutionControlState.REQUIRES_HUMAN,
                    new_graph=None,
                    plan_version=current_version,
                    diagnosis=diagnosis,
                    reason=f"Replanned action '{act_type}' requires explicit human approval",
                )

        # 8. PlanCritic Validation
        cap_ids = [n.action.action_type for n in new_graph.nodes.values() if n.action and n.action.action_type]
        critic_res = self.plan_critic.evaluate_plan(
            graph=new_graph,
            user_goal=user_goal,
            available_capability_ids=cap_ids,
        )

        if critic_res.status.value == "REJECTED":
            logger.warning("PlanCritic rejected replanned graph", task_id=task_id, issues=[i.to_dict() for i in critic_res.issues])
            if wm_task:
                self.working_memory_manager.record_rejected_recovery(
                    task_id, {"graph": new_graph.to_dict(), "critic": critic_res.to_dict(), "reason": "PlanCritic rejected replan"}
                )
                self.working_memory_manager.set_execution_control_state(task_id, ExecutionControlState.BLOCKED.value)
            return ReplanResult(
                control_state=ExecutionControlState.BLOCKED,
                new_graph=None,
                plan_version=current_version,
                diagnosis=diagnosis,
                critic_result=critic_res.to_dict(),
                reason=f"PlanCritic rejected replanned graph: {[i.message for i in critic_res.issues]}",
            )

        # 9. Update Working Memory & Record Replan Event
        new_version = current_version + 1
        if wm_task:
            self.working_memory_manager.increment_plan_version(task_id)
            self.working_memory_manager.record_plan_version(
                task_id=task_id,
                plan_steps=[n.to_dict() for n in new_graph.nodes.values()],
                reason=f"Replanned due to {diagnosis.failure_type.value}: {diagnosis.root_cause}",
            )
            self.working_memory_manager.record_failure_diagnosis(task_id, diagnosis.to_dict())
            self.working_memory_manager.record_successful_recovery(
                task_id, {"plan_version": new_version, "new_graph_id": new_graph.graph_id, "selected_capability": selected_candidate}
            )
            self.working_memory_manager.set_execution_control_state(task_id, ExecutionControlState.REPLAN.value)

        return ReplanResult(
            control_state=ExecutionControlState.REPLAN,
            new_graph=new_graph,
            plan_version=new_version,
            diagnosis=diagnosis,
            critic_result=critic_res.to_dict(),
            reason=f"Successfully generated corrected TaskGraph (v{new_version}) replacing bad action with '{selected_candidate.get('capability_id') if selected_candidate else 'alternative'}'",
        )

    def _determine_search_query(
        self,
        user_goal: str,
        diagnosis: FailureDiagnosis,
        current_graph: TaskGraph,
        wm_task: Optional[WorkingMemoryTask],
    ) -> str:
        """Determines target capability search query from diagnosis evidence."""
        if diagnosis.affected_requirement:
            return diagnosis.affected_requirement
        if wm_task and wm_task.failed_requirements:
            return wm_task.failed_requirements[0]
        # Prefer user_goal for capability discovery search to find domain-relevant capabilities
        return user_goal

    def _build_replanned_graph(
        self,
        task_id: str,
        completed_nodes: List[TaskNode],
        candidate: Dict[str, Any],
        search_query: str,
    ) -> TaskGraph:
        """Constructs a valid TaskGraph retaining completed nodes and wiring new alternative step."""
        new_graph = TaskGraph(task_id=task_id)

        # 1. Add completed nodes to new graph
        last_completed_id = None
        for cnode in completed_nodes:
            # Clear old edges to rebuild clean graph topology
            cnode.in_edges = []
            cnode.out_edges = []
            new_graph.add_node(cnode)
            if last_completed_id:
                edge_id = f"edge_{last_completed_id}_to_{cnode.node_id}"
                edge = TaskEdge(
                    edge_id=edge_id,
                    source_node_id=last_completed_id,
                    target_node_id=cnode.node_id,
                    condition=EdgeCondition.ON_SUCCESS,
                )
                new_graph.add_edge(edge)
            last_completed_id = cnode.node_id

        # 2. Add alternative recovery node
        recovery_node_id = f"node_replan_{uuid.uuid4().hex[:6]}"
        cap_id = candidate.get("capability_id", "alternative_action")
        target_adapter = candidate.get("adapter_id", "Blender")

        new_action = AutomationAction(
            action_id=f"action_{recovery_node_id}",
            action_type=cap_id,
            target_label=target_adapter,
            selector=candidate.get("default_params", {}),
        )

        recovery_node = TaskNode(
            node_id=recovery_node_id,
            title=f"Alternative Action: {cap_id}",
            node_type=NodeType.ACTION,
            action=new_action,
            state=NodeState.PENDING,
            metadata={"replan_source": search_query, "capability_candidate": candidate},
        )
        new_graph.add_node(recovery_node)

        # Wire edge from last completed node (if any) to recovery node
        if last_completed_id:
            edge_id = f"edge_{last_completed_id}_to_{recovery_node_id}"
            edge = TaskEdge(
                edge_id=edge_id,
                source_node_id=last_completed_id,
                target_node_id=recovery_node_id,
                condition=EdgeCondition.ON_SUCCESS,
            )
            new_graph.add_edge(edge)

        new_graph.terminal_node_ids = [recovery_node_id]
        new_graph.validate()
        return new_graph

    def _llm_replan_fallback(
        self,
        task_id: str,
        user_goal: str,
        completed_nodes: List[TaskNode],
        diagnosis: FailureDiagnosis,
        known_bad: List[Dict[str, Any]],
    ) -> Optional[TaskGraph]:
        """Uses LocalModelRouter reasoning workload to generate alternative step if discovery yields no candidates."""
        try:
            router = LocalModelRouter.get_instance()
            decision = router.route(CognitiveWorkloadType.REASONING)
            prompt = (
                f"Propose a replacement executable action for a failed workflow.\n"
                f"User Goal: {user_goal}\n"
                f"Failure Diagnosis: {diagnosis.root_cause}\n"
                f"Known Bad Actions: {json.dumps(known_bad)}\n"
                f"Completed Steps: {[n.title for n in completed_nodes]}\n\n"
                f"Return JSON with keys:\n"
                f"- action_type: string capability identifier\n"
                f"- target_label: string adapter (e.g. 'Blender')\n"
                f"- parameters: dict of parameters\n"
                f"- title: string title\n"
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
            cand = {
                "capability_id": parsed.get("action_type", "blender:set_principled_metallic"),
                "adapter_id": parsed.get("target_label", "Blender"),
                "default_params": parsed.get("parameters", {}),
            }
            return self._build_replanned_graph(
                task_id=task_id,
                completed_nodes=completed_nodes,
                candidate=cand,
                search_query=user_goal,
            )
        except Exception as e:
            logger.warning("LLM replan fallback failed", error=str(e))
            return None
