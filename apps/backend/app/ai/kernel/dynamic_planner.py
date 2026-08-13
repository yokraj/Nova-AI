"""Dynamic Planner generating execution DAGs with parallel waves, retries, approvals, and verification.
"""

from typing import Any, Dict, List
from app.ai.kernel.interfaces import IDynamicPlanner
from app.ai.kernel.models import CapabilityMatch, ExecutionPlan, PlanNode


class DynamicPlanner(IDynamicPlanner):
    """Dynamic Planner building DAG execution plans for intent fulfillment."""

    async def generate_plan(self, goal_data: Dict[str, Any], capabilities: CapabilityMatch) -> ExecutionPlan:
        """Generates an ExecutionPlan with DAG nodes and parallel waves.

        Args:
            goal_data: Goal dictionary.
            capabilities: Resolved CapabilityMatch object.

        Returns:
            ExecutionPlan instance.
        """
        goal_name = goal_data.get("goal", "general_goal")
        raw_query = goal_data.get("raw_query", "")
        intent_type = goal_data.get("intent_type", "general")

        nodes: List[PlanNode] = []
        waves: List[List[str]] = []
        approval_checkpoints: List[str] = []
        verification_steps: List[str] = []

        # Node 1: Context & Setup
        n1 = PlanNode(
            title=f"Analyze intent and context for {goal_name}",
            action_type="context_analysis",
            subsystem="context_engine",
            parameters={"raw_query": raw_query},
            dependencies=[],
            requires_approval=False,
            verification_check="context_merged",
        )
        nodes.append(n1)

        # Node 2: Primary Subsystem Execution
        if "software_copilot" in intent_type:
            n2 = PlanNode(
                title=f"Execute software engineering tasks: {raw_query}",
                action_type="code_generation",
                subsystem="software_copilot",
                parameters={"prompt": raw_query},
                dependencies=[n1.node_id],
                requires_approval=False,
                verification_check="code_compiled",
            )
            nodes.append(n2)
        elif "desktop_automation" in intent_type:
            n2 = PlanNode(
                title=f"Desktop Action: {raw_query}",
                action_type="desktop_action",
                subsystem="desktop_automation",
                parameters={"command": raw_query},
                dependencies=[n1.node_id],
                requires_approval=False,
                verification_check="action_executed",
            )
            nodes.append(n2)
        else:
            n2 = PlanNode(
                title=f"Execute workflow for {goal_name}",
                action_type="agent_execution",
                subsystem="swarm_engine" if capabilities.execution_runtime == "swarm_parallel" else "runtime_coordinator",
                parameters={"goal": raw_query, "agents": capabilities.agents},
                dependencies=[n1.node_id],
                requires_approval=False,
                verification_check="result_produced",
            )
            nodes.append(n2)

        # Node 3: Verification & Synthesis
        n3 = PlanNode(
            title="Verify post-execution result and synthesize voice response",
            action_type="universal_verification",
            subsystem="universal_verifier",
            parameters={"target_node": n2.node_id},
            dependencies=[n2.node_id],
            requires_approval=False,
            verification_check="verification_confirmed",
        )
        nodes.append(n3)

        # Build parallel execution waves
        waves.append([n1.node_id])
        waves.append([n2.node_id])
        waves.append([n3.node_id])

        verification_steps.extend([n1.node_id, n2.node_id, n3.node_id])

        return ExecutionPlan(
            goal=goal_name,
            intent_type=intent_type,
            nodes=nodes,
            waves=waves,
            fallback_nodes={n2.node_id: "fallback_general_executor"},
            retry_policy={"max_retries": 3, "backoff": 1.5},
            approval_checkpoints=approval_checkpoints,
            verification_steps=verification_steps,
            status="created",
        )
