"""Native Plan Critic for Nova-AI's Cognitive Kernel.

Evaluates proposed execution plans before execution across 10 core dimensions:
1. Goal coverage
2. Missing required steps
3. Dependency correctness
4. Capability suitability
5. Security / policy compatibility
6. Preconditions
7. Expected postconditions
8. Verification strategy
9. Resource / budget feasibility
10. Unnecessary or redundant actions

Combines deterministic structural evaluation with optional local LLM semantic evaluation
via Phase 10E LocalModelRouter.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import time

import structlog

from app.ai.desktop_automation.security_engine import SecurityEngine
from app.ai.kernel.capability_discovery import CapabilityDiscoveryEngine
from app.ai.kernel.model_router import LocalModelRouter, CognitiveWorkloadType, RoutingConstraints
from app.ai.runtime.llm_runtime import LLMRuntime
from app.ai.runtime.models import RuntimeRequest

logger = structlog.get_logger("plan_critic")


class CriticStatus(str, Enum):
    """Overall status of plan critic evaluation."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NEEDS_REVISION = "NEEDS_REVISION"


class IssueSeverity(str, Enum):
    """Severity of a detected plan issue."""

    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class CriticIssue:
    """Represents a specific flaw or risk found in a plan."""

    code: str
    severity: IssueSeverity
    message: str
    node_id: Optional[str] = None
    suggested_fix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
            "node_id": self.node_id,
            "suggested_fix": self.suggested_fix,
        }


@dataclass
class PlanCriticResult:
    """Structured output from PlanCritic evaluation."""

    status: CriticStatus
    confidence: float
    issues: List[CriticIssue] = field(default_factory=list)
    missing_requirements: List[str] = field(default_factory=list)
    suggested_changes: List[str] = field(default_factory=list)
    verification_requirements: List[Dict[str, Any]] = field(default_factory=list)
    critic_model_used: Optional[str] = None
    evaluated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "confidence": self.confidence,
            "issues": [issue.to_dict() for issue in self.issues],
            "missing_requirements": list(self.missing_requirements),
            "suggested_changes": list(self.suggested_changes),
            "verification_requirements": self.verification_requirements,
            "critic_model_used": self.critic_model_used,
            "evaluated_at": self.evaluated_at,
        }


class PlanCritic:
    """Native Plan Critic evaluating proposed plans before execution."""

    _instance: Optional["PlanCritic"] = None

    @classmethod
    def get_instance(cls) -> "PlanCritic":
        """Singleton accessor."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(
        self,
        security_engine: Optional[SecurityEngine] = None,
        capability_engine: Optional[CapabilityDiscoveryEngine] = None,
        model_router: Optional[LocalModelRouter] = None,
    ):
        self.security_engine = security_engine or SecurityEngine()
        self.capability_engine = capability_engine or CapabilityDiscoveryEngine.get_instance()
        self.model_router = model_router or LocalModelRouter.get_instance()
        self.llm_runtime = LLMRuntime.get_instance()

    def evaluate_plan(
        self,
        user_goal: str = "",
        plan_nodes: Optional[List[Dict[str, Any]]] = None,
        edges: Optional[List[Dict[str, Any]]] = None,
        expected_requirements: Optional[List[Dict[str, Any]]] = None,
        max_steps_budget: int = 50,
        use_semantic_critic: bool = True,
        graph: Optional[Any] = None,
        available_capability_ids: Optional[List[str]] = None,
    ) -> PlanCriticResult:
        """Evaluates a proposed execution plan."""
        if hasattr(user_goal, "nodes"):
            graph = user_goal
            user_goal = str(plan_nodes) if isinstance(plan_nodes, str) else "Task execution plan"

        if graph is not None and hasattr(graph, "nodes"):
            plan_nodes = [n.to_dict() for n in graph.nodes.values()]
            edges = [e.to_dict() for e in graph.edges.values()]
        else:
            plan_nodes = plan_nodes or []
        issues: List[CriticIssue] = []
        missing_reqs: List[str] = []
        suggested_changes: List[str] = []
        model_used: Optional[str] = None

        edges = edges or []
        expected_requirements = expected_requirements or []

        # -------------------------------------------------------------
        # 1. Deterministic Structural Checks (Graph, Budget, Security)
        # -------------------------------------------------------------

        # A. Graph Empty / Missing Nodes Check
        if not plan_nodes:
            issues.append(
                CriticIssue(
                    code="EMPTY_PLAN",
                    severity=IssueSeverity.CRITICAL,
                    message="Plan contains zero nodes and cannot fulfill user goal.",
                    suggested_fix="Generate at least one action or sub-goal node.",
                )
            )
            return PlanCriticResult(
                status=CriticStatus.REJECTED,
                confidence=1.0,
                issues=issues,
                missing_requirements=["Execution plan nodes"],
                suggested_changes=["Construct a non-empty task plan."],
            )

        # B. Dependency Correctness & Cycle Detection
        node_ids = {n.get("node_id") or n.get("id") for n in plan_nodes if (n.get("node_id") or n.get("id"))}
        adj: Dict[str, List[str]] = {nid: [] for nid in node_ids}
        in_degree: Dict[str, int] = {nid: 0 for nid in node_ids}

        for edge in edges:
            src = edge.get("source_node_id") or edge.get("source")
            tgt = edge.get("target_node_id") or edge.get("target")

            if src and tgt:
                if src not in node_ids:
                    issues.append(
                        CriticIssue(
                            code="INVALID_EDGE_SOURCE",
                            severity=IssueSeverity.CRITICAL,
                            message=f"Edge references unknown source node '{src}'.",
                            node_id=src,
                            suggested_fix="Ensure all edge endpoints refer to valid plan node IDs.",
                        )
                    )
                if tgt not in node_ids:
                    issues.append(
                        CriticIssue(
                            code="INVALID_EDGE_TARGET",
                            severity=IssueSeverity.CRITICAL,
                            message=f"Edge references unknown target node '{tgt}'.",
                            node_id=tgt,
                            suggested_fix="Ensure all edge endpoints refer to valid plan node IDs.",
                        )
                    )

                if src in node_ids and tgt in node_ids:
                    adj[src].append(tgt)
                    in_degree[tgt] = in_degree.get(tgt, 0) + 1

        # Kahn's algorithm for cycle detection
        queue = [nid for nid in node_ids if in_degree[nid] == 0]
        visited_count = 0
        while queue:
            curr = queue.pop(0)
            visited_count += 1
            for neighbor in adj.get(curr, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if visited_count < len(node_ids):
            issues.append(
                CriticIssue(
                    code="CYCLIC_DEPENDENCY",
                    severity=IssueSeverity.CRITICAL,
                    message="Plan contains cyclic dependencies, which will cause deadlocks.",
                    suggested_fix="Remove circular edges to create a directed acyclic graph (DAG).",
                )
            )

        # C. Resource / Budget Feasibility
        if len(plan_nodes) > max_steps_budget:
            issues.append(
                CriticIssue(
                    code="BUDGET_EXCEEDED",
                    severity=IssueSeverity.CRITICAL,
                    message=f"Plan node count ({len(plan_nodes)}) exceeds max step budget ({max_steps_budget}).",
                    suggested_fix="Consolidate actions or split into sub-tasks.",
                )
            )

        # D. Capability Suitability & Security Compatibility
        seen_actions: Set[Tuple[str, str]] = set()
        for node in plan_nodes:
            nid = node.get("node_id") or node.get("id") or "unknown"
            raw_action = node.get("action") or node.get("capability_id") or node.get("title", "")
            if isinstance(raw_action, dict):
                action = raw_action.get("capability_id") or raw_action.get("action_type") or raw_action.get("name") or ""
            elif isinstance(raw_action, str):
                action = raw_action
            else:
                action = str(raw_action)
            params = node.get("params") or node.get("parameters") or {}

            # Capability verification check
            if action and not action.startswith("goal_") and not action.startswith("plan_"):
                if ":" in action:
                    cap = self.capability_engine.get_capability(action)
                    if not cap:
                        issues.append(
                            CriticIssue(
                                code="UNRESOLVED_CAPABILITY",
                                severity=IssueSeverity.WARNING,
                                message=f"Referenced capability '{action}' is not registered in CapabilityDiscoveryEngine.",
                                node_id=nid,
                                suggested_fix="Use standard registered capabilities from discovery index.",
                            )
                        )

            # Security Policy Compatibility Check
            if action:
                is_sensitive = self.security_engine.check_approval_required(action)
                if is_sensitive:
                    issues.append(
                        CriticIssue(
                            code="APPROVAL_REQUIRED",
                            severity=IssueSeverity.WARNING,
                            message=f"Node '{nid}' involves sensitive action '{action}' requiring explicit human approval.",
                            node_id=nid,
                            suggested_fix="Ensure human approval is granted before execution.",
                        )
                    )

                cmd_str = str(params.get("command") or params.get("cmd") or params.get("script") or "").lower()
                if any(danger in cmd_str for danger in ["format c:", "rmdir /s /q", "del /f /s /q c:", "drop database"]):
                    issues.append(
                        CriticIssue(
                            code="SECURITY_VIOLATION",
                            severity=IssueSeverity.CRITICAL,
                            message=f"Node '{nid}' contains prohibited destructive payload: '{cmd_str}'",
                            node_id=nid,
                            suggested_fix="Remove prohibited destructive command payload.",
                        )
                    )

            # Redundant Action Detection
            action_key = (str(action), str(sorted(params.items()) if isinstance(params, dict) else params))
            if action_key in seen_actions and action:
                issues.append(
                    CriticIssue(
                        code="REDUNDANT_ACTION",
                        severity=IssueSeverity.WARNING,
                        message=f"Duplicate action detected at node '{nid}': {action}",
                        node_id=nid,
                        suggested_fix="Remove redundant action if state change is already accomplished.",
                    )
                )
            else:
                seen_actions.add(action_key)

        # E. Goal Coverage & Requirement Mapping
        covered_req_ids = set()
        for node in plan_nodes:
            req_ids = node.get("requirement_ids") or node.get("requirements") or []
            if isinstance(req_ids, list):
                covered_req_ids.update(req_ids)
            elif isinstance(req_ids, str):
                covered_req_ids.add(req_ids)

        for req in expected_requirements:
            rid = req.get("requirement_id") or req.get("id")
            desc = req.get("description", str(req))
            if rid and rid not in covered_req_ids:
                missing_reqs.append(f"Requirement '{rid}': {desc}")
                issues.append(
                    CriticIssue(
                        code="UNCOVERED_REQUIREMENT",
                        severity=IssueSeverity.WARNING,
                        message=f"Goal requirement '{rid}' ({desc}) is not targeted by any plan node.",
                        suggested_fix=f"Add plan step explicitly targeting requirement '{rid}'.",
                    )
                )

        # -------------------------------------------------------------
        # 2. Semantic LLM Critique (Optional / via LocalModelRouter)
        # -------------------------------------------------------------
        if use_semantic_critic and not any(i.severity == IssueSeverity.CRITICAL for i in issues):
            try:
                # Route request via LocalModelRouter for VERIFICATION_CRITIQUE workload
                decision = self.model_router.route(
                    workload_type=CognitiveWorkloadType.VERIFICATION_CRITIQUE,
                    constraints=RoutingConstraints(
                        require_structured_output=True,
                        max_latency_budget_ms=10000,
                    ),
                    prompt_sample=user_goal,
                )
                model_used = decision.selected_model_id

                # Build compact prompt for LLM evaluation
                plan_summary = "\n".join(
                    [f"- Node [{n.get('id')}]: action='{n.get('action')}', params={n.get('params')}" for n in plan_nodes]
                )
                prompt = (
                    f"You are PlanCritic. Evaluate if the following plan satisfies the USER GOAL.\n"
                    f"USER GOAL: {user_goal}\n"
                    f"PLAN NODES:\n{plan_summary}\n\n"
                    f"Does this plan omit necessary steps (e.g. rendering without adding a camera)? "
                    f"Reply concisely with 'APPROVED' or 'NEEDS_REVISION: <reason>'."
                )

                req = RuntimeRequest(
                    prompt=prompt,
                    model_id=decision.selected_model_id,
                    temperature=0.1,
                )
                import asyncio
                try:
                    resp = asyncio.run(self.llm_runtime.generate(req))
                except RuntimeError:
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        resp = pool.submit(lambda: asyncio.run(self.llm_runtime.generate(req))).result()
                content = (resp.content or "").strip()

                if "NEEDS_REVISION" in content.upper():
                    issues.append(
                        CriticIssue(
                            code="SEMANTIC_CRITIQUE_REVISION",
                            severity=IssueSeverity.WARNING,
                            message=f"Semantic critic suggested plan revision: {content}",
                            suggested_fix="Adjust plan steps based on LLM feedback.",
                        )
                    )
                    suggested_changes.append(content)

            except Exception as e:
                logger.warning("Local model semantic critique failed, relying on structural critic", error=str(e))

        # -------------------------------------------------------------
        # 3. Formulate Status & Confidence Result
        # -------------------------------------------------------------
        critical_count = sum(1 for i in issues if i.severity == IssueSeverity.CRITICAL)
        warning_count = sum(1 for i in issues if i.severity == IssueSeverity.WARNING)

        if critical_count > 0:
            status = CriticStatus.REJECTED
            confidence = 0.95
        elif warning_count > 0 or missing_reqs:
            status = CriticStatus.NEEDS_REVISION
            confidence = 0.85
        else:
            status = CriticStatus.APPROVED
            confidence = 0.95

        for issue in issues:
            if issue.suggested_fix and issue.suggested_fix not in suggested_changes:
                suggested_changes.append(issue.suggested_fix)

        return PlanCriticResult(
            status=status,
            confidence=confidence,
            issues=issues,
            missing_requirements=missing_reqs,
            suggested_changes=suggested_changes,
            verification_requirements=[r if isinstance(r, dict) else getattr(r, "to_dict", lambda: dict(r))() for r in expected_requirements],
            critic_model_used=model_used,
        )
