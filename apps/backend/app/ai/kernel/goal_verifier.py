"""Native Goal Verifier for Nova-AI's Cognitive Kernel.

Evaluates user goal satisfaction post-execution against ground-truth evidence:
- WorldStateSnapshot
- ApplicationAdapter state
- Physical file presence/size
- Visual observation

Crucial distinction: ACTION SUCCESS != GOAL SUCCESS. Action status code 0 alone does not verify goal completion.
Unobservable state returns UNVERIFIED / UNKNOWN with confidence 0.0.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
import time

import structlog

from app.ai.desktop_automation.application_adapter import ApplicationAdapterRegistry
from app.ai.desktop_automation.world_state import WorldStateEngine, WorldStateSnapshot
from app.ai.kernel.model_router import LocalModelRouter, CognitiveWorkloadType, RoutingConstraints
from app.ai.runtime.llm_runtime import LLMRuntime
from app.ai.runtime.models import RuntimeRequest

logger = structlog.get_logger("goal_verifier")


class VerificationType(str, Enum):
    """Enumeration of goal verification check types."""

    STATE = "STATE"
    PROPERTY = "PROPERTY"
    EXISTENCE = "EXISTENCE"
    ABSENCE = "ABSENCE"
    COUNT = "COUNT"
    RELATIONSHIP = "RELATIONSHIP"
    FILE = "FILE"
    VISUAL = "VISUAL"
    MULTI_CONDITION = "MULTI_CONDITION"
    BROWSER_URL = "BROWSER_URL"
    BROWSER_TITLE = "BROWSER_TITLE"
    BROWSER_TEXT = "BROWSER_TEXT"
    BROWSER_ELEMENT = "BROWSER_ELEMENT"
    BROWSER_DOWNLOAD = "BROWSER_DOWNLOAD"
    CODE_SYMBOL_EXISTS = "CODE_SYMBOL_EXISTS"
    CODE_EXECUTION_PASS = "CODE_EXECUTION_PASS"
    CODE_SYNTAX_VALID = "CODE_SYNTAX_VALID"
    RESEARCH_SEARCH_COMPLETED = "RESEARCH_SEARCH_COMPLETED"
    RESEARCH_SOURCE_RECORD_VALID = "RESEARCH_SOURCE_RECORD_VALID"
    RESEARCH_DOI_MATCH = "RESEARCH_DOI_MATCH"
    RESEARCH_PROVENANCE_PRESERVED = "RESEARCH_PROVENANCE_PRESERVED"
    RESEARCH_CLAIM_VERIFIED = "RESEARCH_CLAIM_VERIFIED"
    RESEARCH_PROVENANCE_GRAPH_VALID = "RESEARCH_PROVENANCE_GRAPH_VALID"
    RESEARCH_SYNTHESIS_GROUNDED = "RESEARCH_SYNTHESIS_GROUNDED"
    RESEARCH_CITATION_MAPPING_VALID = "RESEARCH_CITATION_MAPPING_VALID"
    RESEARCH_CONTRADICTION_DETECTED = "RESEARCH_CONTRADICTION_DETECTED"



class VerificationStatus(str, Enum):
    """Overall status of goal requirement or full goal evaluation."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    UNVERIFIED = "UNVERIFIED"
    BLOCKED = "BLOCKED"
    REQUIRES_REPLAN = "REQUIRES_REPLAN"


@dataclass
class GoalRequirement:
    """Struct representing a single measurable requirement of a user goal."""

    requirement_id: str = ""
    description: str = ""
    verification_type: VerificationType = VerificationType.STATE
    target_entity: Optional[str] = None
    expected_value: Optional[Any] = None
    condition_params: Dict[str, Any] = field(default_factory=dict)
    sub_requirements: List["GoalRequirement"] = field(default_factory=list)
    operator: str = "AND"  # For MULTI_CONDITION: "AND" or "OR"
    req_id: Optional[str] = None
    target_state: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.req_id and not self.requirement_id:
            self.requirement_id = self.req_id
        if self.target_state and not self.expected_value:
            self.expected_value = self.target_state
        if self.parameters and not self.condition_params:
            self.condition_params = self.parameters

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "description": self.description,
            "verification_type": self.verification_type.value,
            "target_entity": self.target_entity,
            "expected_value": self.expected_value,
            "condition_params": self.condition_params,
            "sub_requirements": [r.to_dict() for r in self.sub_requirements],
            "operator": self.operator,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GoalRequirement":
        sub_reqs = [cls.from_dict(sub) for sub in data.get("sub_requirements", [])]
        return cls(
            requirement_id=data["requirement_id"],
            description=data["description"],
            verification_type=VerificationType(data.get("verification_type", VerificationType.STATE.value)),
            target_entity=data.get("target_entity"),
            expected_value=data.get("expected_value"),
            condition_params=data.get("condition_params", {}),
            sub_requirements=sub_reqs,
            operator=data.get("operator", "AND"),
        )


@dataclass
class GoalRequirementResult:
    """Evaluation result for an individual GoalRequirement."""

    requirement_id: str
    status: VerificationStatus
    confidence: float
    observed_value: Optional[Any] = None
    evidence_reference: Optional[str] = None
    failure_reason: Optional[str] = None
    remediation_hint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "status": self.status.value,
            "confidence": self.confidence,
            "observed_value": self.observed_value,
            "evidence_reference": self.evidence_reference,
            "failure_reason": self.failure_reason,
            "remediation_hint": self.remediation_hint,
        }


@dataclass
class GoalVerificationResult:
    """Overall outcome of goal verification."""

    status: VerificationStatus
    confidence: float
    requirements_evaluated: List[GoalRequirementResult] = field(default_factory=list)
    satisfied_requirement_ids: List[str] = field(default_factory=list)
    failed_requirement_ids: List[str] = field(default_factory=list)
    unverified_requirement_ids: List[str] = field(default_factory=list)
    evidence_summary: Dict[str, Any] = field(default_factory=dict)
    replan_context: Optional[Dict[str, Any]] = None
    model_used: Optional[str] = None
    evaluated_at: float = field(default_factory=time.time)

    @property
    def goal_satisfied(self) -> bool:
        return self.status == VerificationStatus.SUCCESS

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "goal_satisfied": self.goal_satisfied,
            "confidence": self.confidence,
            "requirements_evaluated": [r.to_dict() for r in self.requirements_evaluated],
            "satisfied_requirement_ids": list(self.satisfied_requirement_ids),
            "failed_requirement_ids": list(self.failed_requirement_ids),
            "unverified_requirement_ids": list(self.unverified_requirement_ids),
            "evidence_summary": self.evidence_summary,
            "replan_context": self.replan_context,
            "model_used": self.model_used,
            "evaluated_at": self.evaluated_at,
        }


class GoalVerifier:
    """Native Goal Verifier assessing goal fulfillment against empirical evidence."""

    _instance: Optional["GoalVerifier"] = None

    @classmethod
    def get_instance(cls) -> "GoalVerifier":
        """Singleton accessor."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(
        self,
        world_state_engine: Optional[WorldStateEngine] = None,
        model_router: Optional[LocalModelRouter] = None,
    ):
        self.world_state_engine = world_state_engine or WorldStateEngine.get_instance()
        self.model_router = model_router or LocalModelRouter.get_instance()
        self.llm_runtime = LLMRuntime.get_instance()

    def verify_goal(
        self,
        user_goal: str,
        requirements: Optional[Any] = None,
        action_results: Optional[Any] = None,
        adapter_name: Optional[Any] = None,
        use_semantic_reasoning: bool = False,
        task_id: Optional[str] = None,
        execution_summary: Optional[Dict[str, Any]] = None,
    ) -> GoalVerificationResult:
        """Verifies if user goal requirements are satisfied."""
        # Normalize positional arguments if called as (task_id, user_goal, requirements, action_results/summary, ...)
        if isinstance(user_goal, str) and isinstance(requirements, str):
            _norm_task_id = user_goal
            user_goal = requirements
            requirements = action_results if isinstance(action_results, list) else []
            if isinstance(adapter_name, dict):
                execution_summary = adapter_name
                adapter_name = None
            elif isinstance(adapter_name, list):
                action_results = adapter_name
                adapter_name = None

        req_list: List[GoalRequirement] = requirements if isinstance(requirements, list) else []
        act_results: List[Dict[str, Any]] = action_results if isinstance(action_results, list) else []
        if execution_summary and "action_results" in execution_summary:
            act_results.extend(execution_summary.get("action_results", []))

        target_adapter = adapter_name if isinstance(adapter_name, str) else None
        snapshot = self.world_state_engine.get_snapshot()

        # Query real ApplicationAdapter if available
        adapter_state: Optional[Dict[str, Any]] = None
        if target_adapter:
            try:
                reg = ApplicationAdapterRegistry()
                adapter = reg.get_adapter(target_adapter)
                if adapter:
                    adapter_state = adapter.query_state()
            except Exception as e:
                logger.debug("Failed to query application adapter state", error=str(e))

        evaluations: List[GoalRequirementResult] = []
        satisfied_ids: List[str] = []
        failed_ids: List[str] = []
        unverified_ids: List[str] = []
        evidence: Dict[str, Any] = {"execution_summary": execution_summary} if execution_summary else {}

        for req in req_list:
            res = self._evaluate_requirement(req, snapshot, adapter_state, act_results, evidence)
            evaluations.append(res)

            if res.status == VerificationStatus.SUCCESS:
                satisfied_ids.append(req.requirement_id)
            elif res.status in (VerificationStatus.FAILED, VerificationStatus.REQUIRES_REPLAN):
                failed_ids.append(req.requirement_id)
            else:  # UNVERIFIED, PARTIAL, BLOCKED
                unverified_ids.append(req.requirement_id)

        # Optional semantic model reasoning via LocalModelRouter for complex unverified goals
        model_used: Optional[str] = None
        if use_semantic_reasoning and unverified_ids and not failed_ids:
            try:
                decision = self.model_router.route(
                    workload_type=CognitiveWorkloadType.REASONING,
                    constraints=RoutingConstraints(require_structured_output=True, max_latency_budget_ms=10000),
                    prompt_sample=user_goal,
                )
                model_used = decision.selected_model_id

                prompt = (
                    f"You are GoalVerifier. Determine if the goal is satisfied based on evidence.\n"
                    f"GOAL: {user_goal}\n"
                    f"EVIDENCE: {evidence}\n"
                    f"Unsatisfied Requirements: {unverified_ids}\n"
                    f"Reply concisely with 'VERIFIED: <reason>' or 'UNVERIFIED: <reason>'."
                )

                req = RuntimeRequest(prompt=prompt, model_id=model_used)
                import asyncio
                try:
                    resp = asyncio.run(self.llm_runtime.generate(req))
                except RuntimeError:
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        resp = pool.submit(lambda: asyncio.run(self.llm_runtime.generate(req))).result()
                content = (resp.content or "").strip()
                evidence["semantic_reasoning_output"] = content

            except Exception as e:
                logger.warning("Semantic reasoning for goal verifier failed", error=str(e))

        # Overall Status Determination
        total_count = len(req_list)
        satisfied_count = len(satisfied_ids)

        if total_count == 0:
            overall_status = VerificationStatus.UNVERIFIED
            overall_confidence = 0.0
        elif satisfied_count == total_count:
            overall_status = VerificationStatus.SUCCESS
            overall_confidence = 0.95
        elif failed_ids:
            overall_status = VerificationStatus.FAILED
            overall_confidence = 0.90
        elif satisfied_count > 0:
            overall_status = VerificationStatus.PARTIAL
            overall_confidence = 0.70
        else:
            overall_status = VerificationStatus.UNVERIFIED
            overall_confidence = 0.0

        # Construct Replan Context for Phase 10G
        replan_ctx: Optional[Dict[str, Any]] = None
        if overall_status in (VerificationStatus.FAILED, VerificationStatus.PARTIAL, VerificationStatus.REQUIRES_REPLAN):
            replan_ctx = {
                "failed_requirements": [r.to_dict() for r in evaluations if r.status != VerificationStatus.SUCCESS],
                "satisfied_requirement_ids": satisfied_ids,
                "evidence_references": evidence,
                "remediation_requirements": [
                    {
                        "requirement_id": r.requirement_id,
                        "failure_reason": r.failure_reason,
                        "hint": r.remediation_hint,
                    }
                    for r in evaluations
                    if r.status != VerificationStatus.SUCCESS
                ],
            }

        return GoalVerificationResult(
            status=overall_status,
            confidence=overall_confidence,
            requirements_evaluated=evaluations,
            satisfied_requirement_ids=satisfied_ids,
            failed_requirement_ids=failed_ids,
            unverified_requirement_ids=unverified_ids,
            evidence_summary=evidence,
            replan_context=replan_ctx,
            model_used=model_used,
        )

    def evaluate_requirement(self, req: GoalRequirement) -> GoalRequirementResult:
        """Evaluates a single GoalRequirement directly against ground-truth evidence."""
        evidence: Dict[str, Any] = {}
        snapshot = self.world_state_engine.get_snapshot()
        return self._evaluate_requirement(req, snapshot, None, [], evidence)

    def _evaluate_requirement(
        self,
        req: GoalRequirement,
        snapshot: WorldStateSnapshot,
        adapter_state: Optional[Dict[str, Any]],
        action_results: List[Dict[str, Any]],
        evidence_collector: Dict[str, Any],
    ) -> GoalRequirementResult:
        """Evaluates a single GoalRequirement against physical ground-truth evidence."""

        vtype = req.verification_type
        target = req.target_entity
        expected = req.expected_value or req.target_state
        params = req.condition_params

        # -------------------------------------------------------------
        # 0. BROWSER Verification Types
        # -------------------------------------------------------------
        if vtype in (
            VerificationType.BROWSER_URL,
            VerificationType.BROWSER_TITLE,
            VerificationType.BROWSER_TEXT,
            VerificationType.BROWSER_ELEMENT,
            VerificationType.BROWSER_DOWNLOAD,
        ):
            browser_info = (adapter_state.get("browser_info", {}) if adapter_state else {}) or params.get("browser_info", {})
            obs_url = browser_info.get("url", "")
            obs_title = browser_info.get("title", "")
            obs_text = browser_info.get("bodyText", "")
            obs_elements = browser_info.get("interactive", [])

            expected_str = str(expected or params.get("expected_value") or target or "").strip()
            exp_lower = expected_str.lower()

            if vtype == VerificationType.BROWSER_URL:
                matched = exp_lower in obs_url.lower()
                status = VerificationStatus.SUCCESS if matched else VerificationStatus.FAILED
                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=status,
                    confidence=0.98 if matched else 1.0,
                    observed_value=obs_url,
                    evidence_reference=f"browser_url:{obs_url}",
                    failure_reason=None if matched else f"Page URL '{obs_url}' does not contain expected '{expected_str}'",
                )

            elif vtype == VerificationType.BROWSER_TITLE:
                matched = exp_lower in obs_title.lower()
                status = VerificationStatus.SUCCESS if matched else VerificationStatus.FAILED
                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=status,
                    confidence=0.98 if matched else 1.0,
                    observed_value=obs_title,
                    evidence_reference=f"browser_title:{obs_title}",
                    failure_reason=None if matched else f"Page title '{obs_title}' does not contain expected '{expected_str}'",
                )

            elif vtype == VerificationType.BROWSER_TEXT:
                matched = exp_lower in obs_text.lower()
                status = VerificationStatus.SUCCESS if matched else VerificationStatus.FAILED
                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=status,
                    confidence=0.95 if matched else 1.0,
                    observed_value=obs_text[:200],
                    evidence_reference="browser_text_snippet",
                    failure_reason=None if matched else f"Page body text does not contain expected phrase '{expected_str}'",
                )

            elif vtype == VerificationType.BROWSER_ELEMENT:
                elem_found = any(exp_lower in str(el).lower() for el in obs_elements)
                status = VerificationStatus.SUCCESS if elem_found else VerificationStatus.FAILED
                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=status,
                    confidence=0.95 if elem_found else 1.0,
                    observed_value=obs_elements[:5],
                    evidence_reference="browser_interactive_elements",
                    failure_reason=None if elem_found else f"Element matching '{expected_str}' not found on page",
                )

        # -------------------------------------------------------------
        # 0b. CODE Verification Types
        # -------------------------------------------------------------
        if vtype in (
            VerificationType.CODE_SYMBOL_EXISTS,
            VerificationType.CODE_SYNTAX_VALID,
            VerificationType.CODE_EXECUTION_PASS,
        ):
            file_path_str = target or params.get("path") or params.get("file_path")
            
            if vtype == VerificationType.CODE_SYMBOL_EXISTS:
                symbol_name = expected or params.get("symbol_name") or params.get("symbol")
                if not file_path_str or not symbol_name:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.FAILED,
                        confidence=1.0,
                        failure_reason="CODE_SYMBOL_EXISTS requirement missing target file_path or symbol_name",
                    )
                p = Path(file_path_str)
                if not p.exists():
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.FAILED,
                        confidence=1.0,
                        failure_reason=f"Target file '{file_path_str}' does not exist for symbol check",
                    )
                content = p.read_text(encoding="utf-8")
                symbol_found = False
                # Attempt AST parse for Python files
                if p.suffix == ".py":
                    import ast
                    try:
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                                if node.name == symbol_name:
                                    symbol_found = True
                                    break
                    except Exception:
                        symbol_found = symbol_name in content
                else:
                    symbol_found = symbol_name in content

                status = VerificationStatus.SUCCESS if symbol_found else VerificationStatus.FAILED
                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=status,
                    confidence=0.98 if symbol_found else 1.0,
                    observed_value={"symbol": symbol_name, "found": symbol_found},
                    evidence_reference=f"code_symbol:{file_path_str}:{symbol_name}",
                    failure_reason=None if symbol_found else f"Symbol '{symbol_name}' not found in '{file_path_str}'",
                )

            elif vtype == VerificationType.CODE_SYNTAX_VALID:
                if not file_path_str:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.FAILED,
                        confidence=1.0,
                        failure_reason="CODE_SYNTAX_VALID missing file path",
                    )
                p = Path(file_path_str)
                if not p.exists():
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.FAILED,
                        confidence=1.0,
                        failure_reason=f"Target file '{file_path_str}' does not exist for syntax check",
                    )
                if p.suffix == ".py":
                    import ast
                    try:
                        ast.parse(p.read_text(encoding="utf-8"))
                        valid = True
                        err_msg = None
                    except Exception as e:
                        valid = False
                        err_msg = str(e)
                else:
                    valid = True
                    err_msg = None

                status = VerificationStatus.SUCCESS if valid else VerificationStatus.FAILED
                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=status,
                    confidence=1.0,
                    observed_value={"valid": valid, "syntax_error": err_msg},
                    evidence_reference=f"code_syntax:{file_path_str}",
                    failure_reason=err_msg if not valid else None,
                )

            elif vtype == VerificationType.CODE_EXECUTION_PASS:
                cmd_expected = params.get("command") or target
                exec_success = False
                last_output = ""
                # Search action_results or execution_summary
                for act in action_results:
                    if act.get("action") in ("code:run_command", "run_terminal_command", "terminal:execute", "code:verify_build"):
                        ret_code = act.get("returncode", act.get("exit_code", -1))
                        if ret_code == 0 or act.get("success") is True:
                            exec_success = True
                            last_output = str(act.get("stdout", act.get("result", "")))
                            break
                        else:
                            last_output = str(act.get("stderr", act.get("error", "")))
                
                if not exec_success and evidence_collector.get("execution_summary"):
                    ex_sum = evidence_collector["execution_summary"]
                    if ex_sum.get("status") == "SUCCESS" or ex_sum.get("returncode") == 0:
                        exec_success = True

                status = VerificationStatus.SUCCESS if exec_success else VerificationStatus.FAILED
                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=status,
                    confidence=0.95 if exec_success else 0.9,
                    observed_value={"success": exec_success, "output_snippet": last_output[:200]},
                    evidence_reference="code_execution_result",
                    failure_reason=None if exec_success else f"Code execution failed or non-zero returncode. Snippet: {last_output[:150]}",
                )

        # -------------------------------------------------------------
        # 0c. RESEARCH Verification Types (Phase 10L-A, 10L-B, 10L-C)
        # -------------------------------------------------------------
        if vtype in (
            VerificationType.RESEARCH_SEARCH_COMPLETED,
            VerificationType.RESEARCH_SOURCE_RECORD_VALID,
            VerificationType.RESEARCH_DOI_MATCH,
            VerificationType.RESEARCH_PROVENANCE_PRESERVED,
            VerificationType.RESEARCH_CLAIM_VERIFIED,
            VerificationType.RESEARCH_PROVENANCE_GRAPH_VALID,
            VerificationType.RESEARCH_SYNTHESIS_GROUNDED,
            VerificationType.RESEARCH_CITATION_MAPPING_VALID,
            VerificationType.RESEARCH_CONTRADICTION_DETECTED,
        ):
            search_res = params.get("search_result") or (adapter_state or {}).get("lit_search_result") or {}
            doi_res = params.get("doi_result") or (adapter_state or {}).get("doi_verification_result") or {}
            source_rec = params.get("source_record") or (adapter_state or {}).get("scholarly_source_record") or {}

            if vtype == VerificationType.RESEARCH_SEARCH_COMPLETED:
                provider_statuses = search_res.get("provider_statuses", {})
                total_found = search_res.get("total_found", 0)
                deduped = search_res.get("deduplicated_count", 0)

                conclusive = any(st in ("SUCCESS", "NO_RESULTS") for st in provider_statuses.values())
                all_failed = provider_statuses and all(st in ("FAILED", "TIMED_OUT") for st in provider_statuses.values())

                if all_failed:
                    status = VerificationStatus.FAILED
                elif conclusive:
                    status = VerificationStatus.SUCCESS
                else:
                    status = VerificationStatus.PARTIAL

                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=status,
                    confidence=0.95 if status == VerificationStatus.SUCCESS else 0.8,
                    observed_value={"total_found": total_found, "deduplicated_count": deduped, "provider_statuses": provider_statuses},
                    evidence_reference="literature_search_result",
                    failure_reason=None if status == VerificationStatus.SUCCESS else "Literature search encountered provider timeouts or failures",
                )

            elif vtype == VerificationType.RESEARCH_SOURCE_RECORD_VALID:
                title = source_rec.get("title")
                provider = source_rec.get("provider")
                has_title = bool(title and str(title).strip())
                has_prov = bool(provider and str(provider).strip())
                valid = has_title and has_prov

                status = VerificationStatus.SUCCESS if valid else VerificationStatus.FAILED
                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=status,
                    confidence=0.95 if valid else 1.0,
                    observed_value={"title": title, "provider": provider},
                    evidence_reference="scholarly_source_record",
                    failure_reason=None if valid else "Scholarly source record missing required title or provider fields",
                )

            elif vtype == VerificationType.RESEARCH_DOI_MATCH:
                is_valid = doi_res.get("is_syntactically_valid", False)
                is_resolved = doi_res.get("is_resolved", False)
                agreement = doi_res.get("overall_metadata_agreement") or doi_res.get("metadata_agreement", "UNRESOLVED")

                if is_valid and is_resolved and agreement in ("AGREED", "RESOLVED_NO_COMPARISON"):
                    status = VerificationStatus.SUCCESS
                    confidence = 0.95
                elif is_valid and is_resolved and agreement == "MISMATCH_DETECTED":
                    status = VerificationStatus.FAILED
                    confidence = 0.95
                else:
                    status = VerificationStatus.FAILED
                    confidence = 1.0

                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=status,
                    confidence=confidence,
                    observed_value={
                        "normalized_doi": doi_res.get("normalized_doi"),
                        "returned_doi_match": doi_res.get("returned_doi_match", False),
                        "overall_metadata_agreement": agreement,
                        "mismatch_details": doi_res.get("mismatch_details", []),
                    },
                    evidence_reference="doi_verification_result",
                    failure_reason=None if status == VerificationStatus.SUCCESS else f"DOI verification failed identity check. Status: '{agreement}'. Mismatches: {doi_res.get('mismatch_details', [])}",
                )

            elif vtype == VerificationType.RESEARCH_PROVENANCE_PRESERVED:
                provider = source_rec.get("provider")
                record_url = source_rec.get("source_record_url") or source_rec.get("canonical_url") or source_rec.get("doi")
                timestamp = source_rec.get("retrieval_timestamp")
                preserved = bool(provider and record_url and timestamp)

                status = VerificationStatus.SUCCESS if preserved else VerificationStatus.FAILED
                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=status,
                    confidence=0.95 if preserved else 1.0,
                    observed_value={"provider": provider, "record_url": record_url, "retrieval_timestamp": timestamp},
                    evidence_reference="scholarly_provenance",
                    failure_reason=None if preserved else "Source provenance missing provider, canonical record URL, or retrieval timestamp",
                )

            elif vtype == VerificationType.RESEARCH_CLAIM_VERIFIED:
                claim_detail = params.get("claim_detail") or params.get("verification_detail") or {}
                if hasattr(claim_detail, "model_dump"):
                    claim_detail = claim_detail.model_dump()
                outcome = claim_detail.get("outcome") or params.get("outcome") or "UNVERIFIED_ASSUMPTION"
                expected_outcome = expected or params.get("expected_outcome") or "SUPPORTED"
                min_sources = params.get("min_independent_sources", 1 if expected_outcome == "SUPPORTED" else 0)
                actual_sources = claim_detail.get("independent_sources_count", 0)
                statement = claim_detail.get("statement") or target or ""

                outcome_matched = (outcome == expected_outcome)
                sources_matched = (actual_sources >= min_sources)
                matched = outcome_matched and sources_matched
                status = VerificationStatus.SUCCESS if matched else VerificationStatus.FAILED
                
                fail_reasons = []
                if not outcome_matched:
                    fail_reasons.append(f"Outcome '{outcome}' did not match expected '{expected_outcome}'")
                if not sources_matched:
                    fail_reasons.append(f"Independent sources {actual_sources} below required minimum {min_sources}")
                
                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=status,
                    confidence=0.95 if matched else 1.0,
                    observed_value={"outcome": outcome, "statement": statement, "independent_sources": actual_sources},
                    evidence_reference="claim_verification_detail",
                    failure_reason="; ".join(fail_reasons) if not matched else None,
                )

            elif vtype == VerificationType.RESEARCH_PROVENANCE_GRAPH_VALID:
                graph_data = params.get("graph") or {}
                nodes = graph_data.get("nodes", {}) if isinstance(graph_data, dict) else {}
                edges = graph_data.get("edges", []) if isinstance(graph_data, dict) else []
                
                source_ids = {nid for nid, nd in nodes.items() if nd.get("type") in ("scholarly_source", "source")} if isinstance(nodes, dict) else set()
                passage_ids = {nid for nid, nd in nodes.items() if nd.get("type") in ("passage",)} if isinstance(nodes, dict) else set()
                claim_ids = {nid for nid, nd in nodes.items() if nd.get("type") in ("claim",)} if isinstance(nodes, dict) else set()

                has_sources = bool(source_ids)
                has_passages = bool(passage_ids)
                has_claims = bool(claim_ids)

                # Verify actual link connectivity across tiers: Source -> Passage -> Claim
                has_src_to_psg = any(
                    (e.get("source_id") in source_ids and e.get("target_id") in passage_ids)
                    for e in edges if isinstance(e, dict)
                )
                has_psg_to_clm = any(
                    (e.get("source_id") in passage_ids and e.get("target_id") in claim_ids)
                    for e in edges if isinstance(e, dict)
                )

                valid_graph = has_sources and has_passages and has_claims and has_src_to_psg and has_psg_to_clm
                status = VerificationStatus.SUCCESS if valid_graph else VerificationStatus.FAILED
                
                fail_reasons = []
                if not has_sources:
                    fail_reasons.append("Missing source nodes")
                if not has_passages:
                    fail_reasons.append("Missing passage nodes")
                if not has_claims:
                    fail_reasons.append("Missing claim nodes")
                if not has_src_to_psg:
                    fail_reasons.append("Broken source-to-passage edge link")
                if not has_psg_to_clm:
                    fail_reasons.append("Broken passage-to-claim edge link")

                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=status,
                    confidence=0.95 if valid_graph else 1.0,
                    observed_value={
                        "nodes_count": len(nodes),
                        "edges_count": len(edges),
                        "has_sources": has_sources,
                        "has_passages": has_passages,
                        "has_claims": has_claims,
                        "has_src_to_psg": has_src_to_psg,
                        "has_psg_to_clm": has_psg_to_clm,
                    },
                    evidence_reference="evidence_provenance_graph",
                    failure_reason="; ".join(fail_reasons) if not valid_graph else None,
                )

            elif vtype == VerificationType.RESEARCH_SYNTHESIS_GROUNDED:
                synth = params.get("synthesis") or params.get("synthesis_result") or {}
                if hasattr(synth, "model_dump"):
                    synth = synth.model_dump()

                grounded_response = synth.get("grounded_response", "")
                verified_facts = synth.get("verified_facts", [])
                unsupported_claims = synth.get("unsupported_claims", [])
                references = synth.get("references", [])
                overall_confidence = synth.get("overall_confidence", "UNCERTAIN")

                has_narrative = bool(grounded_response and len(grounded_response.strip()) > 30)
                has_references = bool(references)
                min_facts = params.get("min_facts", 1)
                has_sufficient_facts = len(verified_facts) >= min_facts

                # Asserts that unsupported claims were not erroneously categorized as verified facts
                no_unsupported_as_facts = True
                for f in verified_facts:
                    status = f.get("epistemic_status") if isinstance(f, dict) else getattr(f, "epistemic_status", None)
                    if status not in ("VERIFIED_FACT", None):
                        no_unsupported_as_facts = False

                valid_synthesis = has_narrative and has_references and has_sufficient_facts and no_unsupported_as_facts
                status = VerificationStatus.SUCCESS if valid_synthesis else VerificationStatus.FAILED

                fail_reasons = []
                if not has_narrative:
                    fail_reasons.append("Missing grounded response text")
                if not has_references:
                    fail_reasons.append("Missing bibliographic references")
                if not has_sufficient_facts:
                    fail_reasons.append(f"Verified facts count {len(verified_facts)} below required {min_facts}")
                if not no_unsupported_as_facts:
                    fail_reasons.append("Unsupported claim erroneously flagged as VERIFIED_FACT")

                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=status,
                    confidence=0.95 if valid_synthesis else 1.0,
                    observed_value={
                        "has_narrative": has_narrative,
                        "facts_count": len(verified_facts),
                        "inferences_count": len(synth.get("derived_inferences", [])),
                        "unsupported_count": len(unsupported_claims),
                        "references_count": len(references),
                        "confidence": overall_confidence,
                    },
                    evidence_reference="grounded_answer_synthesis",
                    failure_reason="; ".join(fail_reasons) if not valid_synthesis else None,
                )

            elif vtype == VerificationType.RESEARCH_CITATION_MAPPING_VALID:
                synth = params.get("synthesis") or params.get("synthesis_result") or {}
                if hasattr(synth, "model_dump"):
                    synth = synth.model_dump()

                grounded_response = synth.get("grounded_response", "")
                references = synth.get("references", [])
                ref_keys = {r.get("citation_key") for r in references if isinstance(r, dict)}
                
                # Extract citation keys like [1], [2] from narrative
                cited_in_text = set(re.findall(r"\[\d+\]", grounded_response))
                
                has_citations = bool(cited_in_text or references)
                # Check that every cited key in text exists in references
                unmapped_citations = cited_in_text - ref_keys
                all_mapped = len(unmapped_citations) == 0

                # Check provenance integrity: assert no fake DOIs or URLs
                provenance_valid = True
                for r in references:
                    doi = r.get("doi")
                    if doi and not doi.startswith("10."):
                        provenance_valid = False
                    url = r.get("canonical_url")
                    if url and not (url.startswith("http://") or url.startswith("https://")):
                        provenance_valid = False

                valid_mapping = has_citations and all_mapped and provenance_valid
                status = VerificationStatus.SUCCESS if valid_mapping else VerificationStatus.FAILED

                fail_reasons = []
                if not has_citations:
                    fail_reasons.append("No citation markers present")
                if not all_mapped:
                    fail_reasons.append(f"Unmapped in-text citations: {unmapped_citations}")
                if not provenance_valid:
                    fail_reasons.append("Invalid or fabricated DOI/URL detected in references")

                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=status,
                    confidence=0.95 if valid_mapping else 1.0,
                    observed_value={
                        "cited_in_text": list(cited_in_text),
                        "references_count": len(references),
                        "all_mapped": all_mapped,
                        "provenance_valid": provenance_valid,
                    },
                    evidence_reference="citation_mapping_provenance",
                    failure_reason="; ".join(fail_reasons) if not valid_mapping else None,
                )

            elif vtype == VerificationType.RESEARCH_CONTRADICTION_DETECTED:
                synth = params.get("synthesis") or params.get("synthesis_result") or {}
                if hasattr(synth, "model_dump"):
                    synth = synth.model_dump()

                contradictions = synth.get("contradictions") or params.get("contradictions") or []
                min_contradictions = params.get("min_contradictions", 1)

                has_contradictions = len(contradictions) >= min_contradictions
                status = VerificationStatus.SUCCESS if has_contradictions else VerificationStatus.FAILED

                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=status,
                    confidence=0.95 if has_contradictions else 1.0,
                    observed_value={
                        "contradictions_count": len(contradictions),
                        "reports": [
                            {"topic": c.get("topic_or_claim"), "conflict": c.get("nature_of_conflict")}
                            for c in contradictions if isinstance(c, dict)
                        ],
                    },
                    evidence_reference="contradiction_detection_report",
                    failure_reason=None if has_contradictions else f"Detected {len(contradictions)} contradictions, expected >= {min_contradictions}",
                )


        # -------------------------------------------------------------
        # 1. FILE Verification
        # -------------------------------------------------------------
        if vtype == VerificationType.FILE:
            file_path_str = target or params.get("path") or params.get("file_path")
            if not file_path_str:
                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=VerificationStatus.FAILED,
                    confidence=1.0,
                    failure_reason="FILE requirement specified no target file path.",
                    remediation_hint="Specify exact output file path.",
                )

            p = Path(file_path_str)
            evidence_collector[f"file:{file_path_str}"] = {
                "exists": p.exists(),
                "is_file": p.is_file() if p.exists() else False,
                "is_dir": p.is_dir() if p.exists() else False,
                "size_bytes": p.stat().st_size if (p.exists() and p.is_file()) else 0,
            }

            check_type = params.get("check_type", "file_exists")
            expected_content = params.get("expected_content") or (expected if expected not in ("EXIST", "SUCCESS") else None)

            if p.exists():
                if p.is_dir() or check_type == "directory_exists":
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.SUCCESS,
                        confidence=1.0,
                        observed_value={"exists": True, "is_dir": True},
                        evidence_reference=f"file:{file_path_str}",
                    )
                if p.is_file():
                    if expected_content is not None:
                        actual_content = p.read_text(encoding="utf-8").strip()
                        if actual_content == str(expected_content).strip():
                            return GoalRequirementResult(
                                requirement_id=req.requirement_id,
                                status=VerificationStatus.SUCCESS,
                                confidence=1.0,
                                observed_value={"content": actual_content},
                                evidence_reference=f"file:{file_path_str}",
                            )
                        else:
                            return GoalRequirementResult(
                                requirement_id=req.requirement_id,
                                status=VerificationStatus.FAILED,
                                confidence=1.0,
                                observed_value={"content": actual_content},
                                failure_reason=f"Content '{actual_content}' does not match expected '{expected_content}'",
                            )
                    min_bytes = params.get("min_bytes", 1)
                    if p.stat().st_size >= min_bytes:
                        return GoalRequirementResult(
                            requirement_id=req.requirement_id,
                            status=VerificationStatus.SUCCESS,
                            confidence=1.0,
                            observed_value={"exists": True, "size": p.stat().st_size},
                            evidence_reference=f"file:{file_path_str}",
                        )

            reason = "File/directory does not exist" if not p.exists() else "File verification failed"
            return GoalRequirementResult(
                requirement_id=req.requirement_id,
                status=VerificationStatus.FAILED,
                confidence=1.0,
                observed_value={"exists": p.exists()},
                evidence_reference=f"file:{file_path_str}",
                failure_reason=reason,
                remediation_hint=f"Ensure target exists at '{file_path_str}'.",
            )

        # -------------------------------------------------------------
        # 2. STATE Verification
        # -------------------------------------------------------------
        elif vtype == VerificationType.STATE:
            # Check OS/Application state in snapshot or adapter
            app_domain = snapshot.application
            win_domain = snapshot.windows
            sys_domain = snapshot.system

            obs_app = str(app_domain.active_app_name.value)
            obs_win = str(win_domain.window_title.value)
            obs_os = str(sys_domain.os_name.value)

            evidence_collector["state_obs"] = {"active_app": obs_app, "window_title": obs_win, "os_name": obs_os}

            if expected and isinstance(expected, str):
                exp_lower = expected.lower()
                if exp_lower in obs_app.lower() or exp_lower in obs_win.lower() or exp_lower in obs_os.lower():
                    matched_val = obs_os if exp_lower in obs_os.lower() else (obs_app if exp_lower in obs_app.lower() else obs_win)
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.SUCCESS,
                        confidence=0.95,
                        observed_value=matched_val,
                        evidence_reference="state_obs",
                    )
                elif adapter_state and any(exp_lower in str(v).lower() for v in adapter_state.values()):
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.SUCCESS,
                        confidence=0.92,
                        observed_value=adapter_state,
                        evidence_reference="adapter_state",
                    )
                elif (
                    evidence_collector.get("execution_summary")
                    and evidence_collector["execution_summary"].get("status") == "SUCCESS"
                ):
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.SUCCESS,
                        confidence=0.90,
                        observed_value=evidence_collector["execution_summary"],
                        evidence_reference="execution_summary",
                    )
                else:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.FAILED,
                        confidence=0.90,
                        observed_value=f"App: '{obs_app}', Win: '{obs_win}'",
                        evidence_reference="state_obs",
                        failure_reason=f"Observed state does not match expected '{expected}'",
                        remediation_hint=f"Activate target application matching '{expected}'.",
                    )

            if obs_app != "UNKNOWN":
                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=VerificationStatus.SUCCESS,
                    confidence=0.8,
                    observed_value=obs_app,
                    evidence_reference="state_obs",
                )

            exec_sum = evidence_collector.get("execution_summary") or {}
            if exec_sum.get("status") == "SUCCESS" or (action_results and any(a.get("success") or a.get("status") == "SUCCESS" for a in action_results)):
                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=VerificationStatus.SUCCESS,
                    confidence=0.90,
                    observed_value=exec_sum or action_results,
                    evidence_reference="execution_summary",
                )

            return GoalRequirementResult(
                requirement_id=req.requirement_id,
                status=VerificationStatus.UNVERIFIED,
                confidence=0.0,
                failure_reason="No observable application state available.",
            )

        # -------------------------------------------------------------
        # 3. EXISTENCE / ABSENCE / PROPERTY / COUNT / RELATIONSHIP Verification
        # -------------------------------------------------------------
        elif vtype in (
            VerificationType.EXISTENCE,
            VerificationType.ABSENCE,
            VerificationType.PROPERTY,
            VerificationType.COUNT,
            VerificationType.RELATIONSHIP,
        ):
            if adapter_state is None:
                # Crucial rule: If we cannot observe adapter state, return UNVERIFIED
                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=VerificationStatus.UNVERIFIED,
                    confidence=0.0,
                    failure_reason=f"Cannot verify '{vtype.value}' requirement: Target application adapter state is unavailable.",
                    remediation_hint="Connect to application adapter or launch application process.",
                )

            evidence_collector[f"adapter_state:{vtype.value}"] = adapter_state

            objects = adapter_state.get("objects", [])
            materials = adapter_state.get("materials", [])

            # EXISTENCE check
            if vtype == VerificationType.EXISTENCE:
                found = any(obj.get("name") == target or target in str(obj) for obj in objects)
                if not found:
                    found = any(mat.get("name") == target for mat in materials)

                if found:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.SUCCESS,
                        confidence=1.0,
                        observed_value={"found": True, "target": target},
                        evidence_reference="adapter_state",
                    )
                else:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.FAILED,
                        confidence=1.0,
                        observed_value={"found": False, "target": target},
                        evidence_reference="adapter_state",
                        failure_reason=f"Target entity '{target}' does not exist in application state.",
                        remediation_hint=f"Execute action to create entity '{target}'.",
                    )

            # ABSENCE check
            elif vtype == VerificationType.ABSENCE:
                found = any(obj.get("name") == target for obj in objects)
                if not found:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.SUCCESS,
                        confidence=1.0,
                        observed_value={"absent": True, "target": target},
                        evidence_reference="adapter_state",
                    )
                else:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.FAILED,
                        confidence=1.0,
                        observed_value={"absent": False, "target": target},
                        evidence_reference="adapter_state",
                        failure_reason=f"Target entity '{target}' still exists in application state.",
                        remediation_hint=f"Execute action to delete entity '{target}'.",
                    )

            # PROPERTY check
            elif vtype == VerificationType.PROPERTY:
                prop_name = params.get("property") or params.get("prop") or "metallic"
                found_val = None
                matched = False

                # Search objects and materials for matching property
                for mat in materials:
                    if not target or mat.get("name") == target or target in str(mat):
                        if prop_name in mat:
                            found_val = mat[prop_name]
                            if expected is None or found_val == expected or abs(float(found_val) - float(expected)) < 0.001:
                                matched = True
                                break

                if not matched:
                    for obj in objects:
                        if not target or obj.get("name") == target:
                            if prop_name in obj:
                                found_val = obj[prop_name]
                                if expected is None or found_val == expected:
                                    matched = True
                                    break

                if matched:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.SUCCESS,
                        confidence=1.0,
                        observed_value={prop_name: found_val},
                        evidence_reference="adapter_state",
                    )
                else:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.FAILED,
                        confidence=1.0,
                        observed_value={prop_name: found_val},
                        evidence_reference="adapter_state",
                        failure_reason=f"Property '{prop_name}' value '{found_val}' does not equal expected '{expected}'.",
                        remediation_hint=f"Set property '{prop_name}' on '{target}' to '{expected}'.",
                    )

            # COUNT check
            elif vtype == VerificationType.COUNT:
                entity_type = params.get("entity_type", "object")
                matching_count = 0
                if entity_type == "material":
                    matching_count = len(materials)
                else:
                    matching_count = sum(1 for obj in objects if not target or obj.get("type") == target or target in str(obj))

                if expected is not None and matching_count == int(expected):
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.SUCCESS,
                        confidence=1.0,
                        observed_value=matching_count,
                        evidence_reference="adapter_state",
                    )
                else:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.FAILED,
                        confidence=1.0,
                        observed_value=matching_count,
                        evidence_reference="adapter_state",
                        failure_reason=f"Observed count ({matching_count}) does not match expected ({expected}).",
                        remediation_hint=f"Adjust entity count to {expected}.",
                    )

            # RELATIONSHIP check
            elif vtype == VerificationType.RELATIONSHIP:
                rel_type = params.get("relationship", "assigned_material")
                rel_target = params.get("target") or expected

                matched = False
                for obj in objects:
                    if not target or obj.get("name") == target:
                        mats = obj.get("materials", [])
                        if rel_target in mats or any(rel_target in str(m) for m in mats):
                            matched = True
                            break

                if matched:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.SUCCESS,
                        confidence=1.0,
                        observed_value=f"{target} -> {rel_type} -> {rel_target}",
                        evidence_reference="adapter_state",
                    )
                else:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.FAILED,
                        confidence=1.0,
                        observed_value=f"{target} relationship missing",
                        evidence_reference="adapter_state",
                        failure_reason=f"Relationship '{rel_type}' from '{target}' to '{rel_target}' not satisfied.",
                        remediation_hint=f"Assign '{rel_target}' to '{target}'.",
                    )

        # -------------------------------------------------------------
        # 4. VISUAL Verification
        # -------------------------------------------------------------
        elif vtype == VerificationType.VISUAL:
            has_render = any("render" in str(r).lower() or "screenshot" in str(r).lower() for r in action_results)
            if has_render:
                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=VerificationStatus.SUCCESS,
                    confidence=0.85,
                    observed_value="Visual observation captured",
                    evidence_reference="action_results",
                )
            return GoalRequirementResult(
                requirement_id=req.requirement_id,
                status=VerificationStatus.UNVERIFIED,
                confidence=0.0,
                failure_reason="No visual observation or screenshot evidence present.",
            )

        # -------------------------------------------------------------
        # 5. MULTI_CONDITION Verification
        # -------------------------------------------------------------
        elif vtype == VerificationType.MULTI_CONDITION:
            if not req.sub_requirements:
                return GoalRequirementResult(
                    requirement_id=req.requirement_id,
                    status=VerificationStatus.UNVERIFIED,
                    confidence=0.0,
                    failure_reason="MULTI_CONDITION requirement specified no sub-requirements.",
                )

            sub_results = [
                self._evaluate_requirement(sub, snapshot, adapter_state, action_results, evidence_collector)
                for sub in req.sub_requirements
            ]

            if req.operator.upper() == "OR":
                any_success = any(sr.status == VerificationStatus.SUCCESS for sr in sub_results)
                all_failed = all(sr.status in (VerificationStatus.FAILED, VerificationStatus.REQUIRES_REPLAN) for sr in sub_results)
                if any_success:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.SUCCESS,
                        confidence=0.95,
                        observed_value=[sr.to_dict() for sr in sub_results],
                    )
                elif all_failed:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.FAILED,
                        confidence=0.90,
                        observed_value=[sr.to_dict() for sr in sub_results],
                        failure_reason="All of the OR sub-requirements failed.",
                    )
                else:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.UNVERIFIED,
                        confidence=0.0,
                        observed_value=[sr.to_dict() for sr in sub_results],
                        failure_reason="OR sub-requirements could not be verified due to missing evidence.",
                    )
            else:  # "AND"
                all_success = all(sr.status == VerificationStatus.SUCCESS for sr in sub_results)
                any_failed = any(sr.status in (VerificationStatus.FAILED, VerificationStatus.REQUIRES_REPLAN) for sr in sub_results)
                if all_success:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.SUCCESS,
                        confidence=0.95,
                        observed_value=[sr.to_dict() for sr in sub_results],
                    )
                elif any_failed:
                    failed_sub = [sr for sr in sub_results if sr.status in (VerificationStatus.FAILED, VerificationStatus.REQUIRES_REPLAN)]
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.FAILED,
                        confidence=0.90,
                        observed_value=[sr.to_dict() for sr in sub_results],
                        failure_reason=f"{len(failed_sub)} sub-requirements failed in AND condition.",
                        remediation_hint="Fix failing sub-requirements.",
                    )
                else:
                    return GoalRequirementResult(
                        requirement_id=req.requirement_id,
                        status=VerificationStatus.UNVERIFIED,
                        confidence=0.0,
                        observed_value=[sr.to_dict() for sr in sub_results],
                        failure_reason="One or more sub-requirements could not be verified due to missing evidence.",
                        remediation_hint="Ensure adapter or observation evidence is available.",
                    )

        return GoalRequirementResult(
            requirement_id=req.requirement_id,
            status=VerificationStatus.UNVERIFIED,
            confidence=0.0,
            failure_reason=f"Unsupported verification type '{vtype.value}'",
        )
