"""Dedicated test suite for Phase 10F Plan Critic + Goal Verifier layer.

Verifies:
- PlanCritic structural and semantic plan evaluation (10 dimensions)
- GoalVerifier multi-type goal verification (9 types)
- Action success != Goal success demonstration
- Action success == Goal success demonstration
- Unobservable state returns UNVERIFIED / UNKNOWN with 0.0 confidence
- WorkingMemory and WorldState integration
- LocalModelRouter integration
- Deterministic verification and evidence traceability with replan context
- Real Ollama model inference for critique and verification
"""

from pathlib import Path
import tempfile
import pytest

from app.ai.desktop_automation.world_state import WorldStateEngine
from app.ai.kernel.goal_verifier import (
    GoalRequirement,
    GoalVerificationResult,
    GoalVerifier,
    VerificationStatus,
    VerificationType,
)
from app.ai.kernel.plan_critic import (
    CriticStatus,
    PlanCritic,
    PlanCriticResult,
)
from app.ai.memory.working_memory import WorkingMemoryManager


class TestCognitivePlanCriticAndVerifier:
    """Test suite covering Phase 10F PlanCritic and GoalVerifier functionality."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.critic = PlanCritic()
        self.verifier = GoalVerifier()
        self.wm_manager = WorkingMemoryManager.get_instance()
        self.world_state_engine = WorldStateEngine.get_instance()

    def test_1_simple_state_goal_verification(self):
        """1. Verify simple STATE goal requirement against WorldState."""
        req = GoalRequirement(
            requirement_id="req_state_1",
            description="Verify system elevated status or app name",
            verification_type=VerificationType.STATE,
            expected_value="Windows",
        )
        res = self.verifier.verify_goal(
            user_goal="Check OS state",
            requirements=[req],
        )
        assert res.status == VerificationStatus.SUCCESS
        assert "req_state_1" in res.satisfied_requirement_ids
        assert res.confidence >= 0.8

    def test_2_property_goal_verification(self):
        """2. Verify PROPERTY goal requirement against mock adapter state."""
        req = GoalRequirement(
            requirement_id="req_prop_1",
            description="Material metallic property set to 1.0",
            verification_type=VerificationType.PROPERTY,
            target_entity="PrincipledMaterial",
            expected_value=1.0,
            condition_params={"property": "metallic"},
        )
        # Mock adapter state
        mock_adapter_state = {
            "materials": [{"name": "PrincipledMaterial", "metallic": 1.0}]
        }
        res = self.verifier._evaluate_requirement(
            req=req,
            snapshot=self.world_state_engine.get_snapshot(),
            adapter_state=mock_adapter_state,
            action_results=[],
            evidence_collector={},
        )
        assert res.status == VerificationStatus.SUCCESS
        assert res.confidence == 1.0
        assert res.observed_value == {"metallic": 1.0}

    def test_3_multi_condition_goal_verification(self):
        """3. Verify MULTI_CONDITION requirement combining AND / OR sub-requirements."""
        sub1 = GoalRequirement(
            requirement_id="sub_1",
            description="Camera exists",
            verification_type=VerificationType.EXISTENCE,
            target_entity="Camera",
        )
        sub2 = GoalRequirement(
            requirement_id="sub_2",
            description="Light exists",
            verification_type=VerificationType.EXISTENCE,
            target_entity="Light",
        )
        multi_req = GoalRequirement(
            requirement_id="req_multi_1",
            description="Camera and Light both exist",
            verification_type=VerificationType.MULTI_CONDITION,
            sub_requirements=[sub1, sub2],
            operator="AND",
        )
        mock_adapter_state = {
            "objects": [{"name": "Camera", "type": "CAMERA"}, {"name": "Light", "type": "LIGHT"}]
        }

        res = self.verifier.verify_goal(
            user_goal="Verify scene setup",
            requirements=[multi_req],
            adapter_name=None,
        )
        assert res.status == VerificationStatus.UNVERIFIED
        # Manually evaluate against mock state
        eval_res = self.verifier._evaluate_requirement(
            req=multi_req,
            snapshot=self.world_state_engine.get_snapshot(),
            adapter_state=mock_adapter_state,
            action_results=[],
            evidence_collector={},
        )
        assert eval_res.status == VerificationStatus.SUCCESS

    def test_4_failed_action_verification(self):
        """4. Verify goal failure when action reports failure and target state is not met."""
        req = GoalRequirement(
            requirement_id="req_file_1",
            description="Non-existent output file",
            verification_type=VerificationType.FILE,
            target_entity="C:/invalid_nonexistent_directory/output.png",
        )
        action_results = [{"action_id": "render_1", "status": "failed", "error": "Disk error"}]

        res = self.verifier.verify_goal(
            user_goal="Render to file",
            requirements=[req],
            action_results=action_results,
        )
        assert res.status == VerificationStatus.FAILED
        assert "req_file_1" in res.failed_requirement_ids
        assert res.replan_context is not None

    def test_5_action_success_differs_from_goal_success(self):
        """5. Crucial demonstration: ACTION SUCCESS != GOAL SUCCESS.

        Action API returns status 200/success, but state inspection shows property value is wrong.
        """
        # Action reported API success
        action_results = [
            {
                "action_id": "blender:set_principled_metallic",
                "status": "success",
                "output": "API set_principled_metallic executed successfully",
                "verified": True,
            }
        ]

        # But real scene adapter state shows metallic is still 0.0 (e.g. applied to wrong object)
        mock_adapter_state = {
            "materials": [{"name": "PrincipledMaterial", "metallic": 0.0}]
        }

        req = GoalRequirement(
            requirement_id="req_metallic",
            description="Material metallic value set to 1.0",
            verification_type=VerificationType.PROPERTY,
            target_entity="PrincipledMaterial",
            expected_value=1.0,
            condition_params={"property": "metallic"},
        )

        res = self.verifier._evaluate_requirement(
            req=req,
            snapshot=self.world_state_engine.get_snapshot(),
            adapter_state=mock_adapter_state,
            action_results=action_results,
            evidence_collector={},
        )

        # Confirm ACTION SUCCESS (True) != GOAL SUCCESS (FAILED)
        assert action_results[0]["status"] == "success"
        assert res.status == VerificationStatus.FAILED
        assert "does not equal expected" in res.failure_reason

    def test_6_action_success_matches_goal_success(self):
        """6. Demonstration: ACTION SUCCESS == GOAL SUCCESS.

        Action API succeeded AND physical state inspection confirms expected property value.
        """
        action_results = [
            {
                "action_id": "blender:set_principled_metallic",
                "status": "success",
                "output": "API executed",
            }
        ]
        mock_adapter_state = {
            "materials": [{"name": "PrincipledMaterial", "metallic": 1.0}]
        }
        req = GoalRequirement(
            requirement_id="req_metallic",
            description="Material metallic value set to 1.0",
            verification_type=VerificationType.PROPERTY,
            target_entity="PrincipledMaterial",
            expected_value=1.0,
            condition_params={"property": "metallic"},
        )

        res = self.verifier._evaluate_requirement(
            req=req,
            snapshot=self.world_state_engine.get_snapshot(),
            adapter_state=mock_adapter_state,
            action_results=action_results,
            evidence_collector={},
        )
        assert res.status == VerificationStatus.SUCCESS

    def test_7_unknown_unobservable_state_returns_unverified(self):
        """7. Verify unobservable state returns UNVERIFIED with confidence 0.0, zero synthetic success."""
        req = GoalRequirement(
            requirement_id="req_exist_1",
            description="Verify unobservable internal object",
            verification_type=VerificationType.EXISTENCE,
            target_entity="HiddenObject",
        )
        # Adapter state is None (unobservable)
        res = self.verifier._evaluate_requirement(
            req=req,
            snapshot=self.world_state_engine.get_snapshot(),
            adapter_state=None,
            action_results=[],
            evidence_collector={},
        )
        assert res.status == VerificationStatus.UNVERIFIED
        assert res.confidence == 0.0
        assert "unavailable" in res.failure_reason.lower()

    def test_8_missing_plan_requirement_detection(self):
        """8. Test PlanCritic detecting missing/uncovered goal requirements."""
        plan_nodes = [{"id": "node_1", "action": "blender:create_object", "params": {"type": "CUBE"}}]
        expected_reqs = [
            {"requirement_id": "R1", "description": "Create cube"},
            {"requirement_id": "R2", "description": "Create camera and render"},
        ]
        res = self.critic.evaluate_plan(
            user_goal="Create cube and render with camera",
            plan_nodes=plan_nodes,
            expected_requirements=expected_reqs,
            use_semantic_critic=False,
        )
        assert res.status == CriticStatus.NEEDS_REVISION
        assert any("R2" in req for req in res.missing_requirements)

    def test_9_invalid_dependency_graph_critique(self):
        """9. Test PlanCritic rejecting cyclic dependencies in plan graphs."""
        plan_nodes = [
            {"id": "node_1", "action": "step_1"},
            {"id": "node_2", "action": "step_2"},
        ]
        edges = [
            {"source_node_id": "node_1", "target_node_id": "node_2"},
            {"source_node_id": "node_2", "target_node_id": "node_1"},  # Cycle!
        ]
        res = self.critic.evaluate_plan(
            user_goal="Run cyclic process",
            plan_nodes=plan_nodes,
            edges=edges,
            use_semantic_critic=False,
        )
        assert res.status == CriticStatus.REJECTED
        assert any(i.code == "CYCLIC_DEPENDENCY" for i in res.issues)

    def test_10_unnecessary_redundant_action_detection(self):
        """10. Test PlanCritic warning about duplicate/redundant actions."""
        plan_nodes = [
            {"id": "node_1", "action": "blender:create_object", "params": {"name": "Cube"}},
            {"id": "node_2", "action": "blender:create_object", "params": {"name": "Cube"}},  # Duplicate!
        ]
        res = self.critic.evaluate_plan(
            user_goal="Create object",
            plan_nodes=plan_nodes,
            use_semantic_critic=False,
        )
        assert any(i.code == "REDUNDANT_ACTION" for i in res.issues)

    def test_11_visual_verification_with_observation(self):
        """11. Test VISUAL requirement verification when action outputs contain render/screenshot."""
        req = GoalRequirement(
            requirement_id="req_vis_1",
            description="Visual render verification",
            verification_type=VerificationType.VISUAL,
        )
        action_results = [{"action_id": "blender:render_frame", "status": "success", "output": "render_output.png"}]
        res = self.verifier.verify_goal(
            user_goal="Render scene visually",
            requirements=[req],
            action_results=action_results,
        )
        assert res.status == VerificationStatus.SUCCESS

    def test_12_output_file_verification(self):
        """12. Test FILE verification against actual physical file on disk."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(b"PNG_HEADER_DATA_CONTENT")
            tmp_path = tmp.name

        try:
            req = GoalRequirement(
                requirement_id="req_file_temp",
                description="Output PNG file exists",
                verification_type=VerificationType.FILE,
                target_entity=tmp_path,
                condition_params={"min_bytes": 10},
            )
            res = self.verifier.verify_goal(
                user_goal="Export PNG file",
                requirements=[req],
            )
            assert res.status == VerificationStatus.SUCCESS
            assert res.requirements_evaluated[0].observed_value["size"] > 10
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_13_critic_approval(self):
        """13. Test PlanCritic approving a valid execution plan."""
        plan_nodes = [
            {"id": "node_1", "action": "blender:create_camera", "params": {}, "requirement_ids": ["R1"]},
            {"id": "node_2", "action": "blender:render_frame", "params": {}, "requirement_ids": ["R2"]},
        ]
        edges = [{"source_node_id": "node_1", "target_node_id": "node_2"}]
        expected_reqs = [
            {"requirement_id": "R1", "description": "Create camera"},
            {"requirement_id": "R2", "description": "Render frame"},
        ]
        res = self.critic.evaluate_plan(
            user_goal="Create camera and render",
            plan_nodes=plan_nodes,
            edges=edges,
            expected_requirements=expected_reqs,
            use_semantic_critic=False,
        )
        assert res.status == CriticStatus.APPROVED
        assert res.confidence >= 0.9

    def test_14_critic_rejection(self):
        """14. Test PlanCritic rejecting plan due to security policy violation."""
        plan_nodes = [
            {
                "id": "node_sec",
                "action": "system:execute_command",
                "params": {"command": "format C: /q"},  # Dangerous command
            }
        ]
        res = self.critic.evaluate_plan(
            user_goal="Malicious execution attempt",
            plan_nodes=plan_nodes,
            use_semantic_critic=False,
        )
        assert res.status == CriticStatus.REJECTED
        assert any(i.code == "SECURITY_VIOLATION" for i in res.issues)

    def test_15_critic_needs_revision(self):
        """15. Test PlanCritic returning NEEDS_REVISION for missing requirement targeting."""
        plan_nodes = [{"id": "n1", "action": "blender:create_object"}]
        expected_reqs = [{"requirement_id": "REQ_X", "description": "Missing step"}]

        res = self.critic.evaluate_plan(
            user_goal="Execute task with missing requirement",
            plan_nodes=plan_nodes,
            expected_requirements=expected_reqs,
            use_semantic_critic=False,
        )
        assert res.status == CriticStatus.NEEDS_REVISION

    def test_16_working_memory_integration(self):
        """16. Test storing PlanCritic and GoalVerifier outputs in WorkingMemoryTask."""
        task_id = "test_wm_phase10f_task"
        _ = self.wm_manager.create_task(task_id, "WorkingMemory Phase 10F Test")

        critic_res = PlanCriticResult(
            status=CriticStatus.APPROVED,
            confidence=0.95,
            issues=[],
            missing_requirements=[],
            suggested_changes=[],
        )
        self.wm_manager.record_critic_result(task_id, critic_res.to_dict())

        verif_res = GoalVerificationResult(
            status=VerificationStatus.SUCCESS,
            confidence=0.95,
            satisfied_requirement_ids=["R1"],
            failed_requirement_ids=[],
            unverified_requirement_ids=[],
        )
        self.wm_manager.record_goal_verification_details(task_id, verif_res.to_dict())

        snap = self.wm_manager.get_snapshot(task_id)
        assert snap["critic_result"]["status"] == "APPROVED"
        assert snap["goal_verification_status"] == "SUCCESS"
        assert snap["verification_attempt_count"] == 1

        self.wm_manager.clear_task(task_id)

    def test_17_world_state_integration(self):
        """17. Test GoalVerifier drawing real ground-truth from WorldStateEngine."""
        req = GoalRequirement(
            requirement_id="req_ws_1",
            description="Verify elevated system state",
            verification_type=VerificationType.STATE,
            expected_value="Windows",
        )
        res = self.verifier.verify_goal("Check OS", [req])
        assert res.evidence_summary.get("state_obs") is not None

    def test_18_model_router_integration(self):
        """18. Test PlanCritic using LocalModelRouter for semantic evaluation."""
        plan_nodes = [{"id": "node_1", "action": "blender:create_object", "params": {"type": "CUBE"}}]
        res = self.critic.evaluate_plan(
            user_goal="Create a simple cube in Blender",
            plan_nodes=plan_nodes,
            use_semantic_critic=True,
        )
        assert res.critic_model_used is not None
        assert res.status in (CriticStatus.APPROVED, CriticStatus.NEEDS_REVISION)

    def test_19_deterministic_verification(self):
        """19. Test pure deterministic verification without LLM calls."""
        req = GoalRequirement(
            requirement_id="req_det_1",
            description="Deterministic file existence check",
            verification_type=VerificationType.FILE,
            target_entity=str(Path(__file__).resolve()),
        )
        res = self.verifier.verify_goal(
            user_goal="Verify test file exists",
            requirements=[req],
            use_semantic_reasoning=False,
        )
        assert res.status == VerificationStatus.SUCCESS
        assert res.model_used is None

    def test_20_evidence_traceability_and_replan_context(self):
        """20. Test evidence traceability and replan context generation for failed requirements."""
        req1 = GoalRequirement(
            requirement_id="req_fail_1",
            description="Missing target file",
            verification_type=VerificationType.FILE,
            target_entity="C:/nonexistent_file.obj",
        )
        res = self.verifier.verify_goal(
            user_goal="Trace failed evidence",
            requirements=[req1],
        )
        assert res.status == VerificationStatus.FAILED
        assert res.replan_context is not None
        assert "failed_requirements" in res.replan_context
        assert "remediation_requirements" in res.replan_context
        assert res.replan_context["remediation_requirements"][0]["requirement_id"] == "req_fail_1"

    def test_21_real_ollama_model_critique_and_verification(self):
        """21. Execute real local Ollama (qwen3:8b) model for semantic plan critique and verification."""
        user_goal = "Build a 3D animated solar system in Blender and render a high-quality animation frame."
        plan_nodes = [
            {"id": "step_1", "action": "blender:create_object", "params": {"type": "SPHERE", "name": "Sun"}},
            {"id": "step_2", "action": "blender:create_object", "params": {"type": "SPHERE", "name": "Earth"}},
            {"id": "step_3", "action": "blender:render_frame", "params": {"output_path": "solar_system.png"}},
        ]
        # Notice step 3 renders without adding a Camera!
        critic_res = self.critic.evaluate_plan(
            user_goal=user_goal,
            plan_nodes=plan_nodes,
            use_semantic_critic=True,
        )
        assert critic_res.critic_model_used is not None
        print(f"\n[Real Model Phase 10F Test] PlanCritic model used: {critic_res.critic_model_used}")
        print(f"[Real Model Phase 10F Test] Status: {critic_res.status.value}")
        print(f"[Real Model Phase 10F Test] Issues: {[i.message for i in critic_res.issues]}")
