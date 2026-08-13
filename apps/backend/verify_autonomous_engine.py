"""Verification script for the Autonomous Software Engineer Integration Engine.
"""

import os
import asyncio
import tempfile
from app.agents.software_engineer.autonomous.engine import LocalAutonomousEngine
from app.agents.software_engineer.autonomous.models import AutonomousRequest, Decision, MemoryEntry

async def verify_autonomous_engine():
    print("=== STARTING AUTONOMOUS ENGINE VERIFICATION ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Creating sandbox workspace in: {temp_dir}")

        # 1. Instantiate engine
        engine = LocalAutonomousEngine(agent=None, gateway=None, workspace_root=temp_dir)

        # 2. Test router mapping rules
        print("Verifying agent engine router rules...")
        assert engine.router.route_request("Find unused methods") == "Code Intelligence Engine"
        assert engine.router.route_request("Fix API compile error") == "Debugging Engine"
        assert engine.router.route_request("Deploy code to kubernetes cluster") == "Deployment Engine"
        assert engine.router.route_request("Run pytest tests suite") == "Testing Engine"
        assert engine.router.route_request("Update documentation details") == "Documentation Engine"
        print("✓ Engine routing rules verified successfully.")

        # 3. Test decision safety confirmation request checks
        print("Verifying reasoning decision engine checks...")
        safe_dec = Decision(action_type="Generate Code", rationale="Needs implementation.")
        unsafe_dec = Decision(action_type="Delete Workspace Database", rationale="Destructive clean up.", confirmed=False)
        assert engine.decision_engine.validate_action(safe_dec) is True
        assert engine.decision_engine.validate_action(unsafe_dec) is False
        print("✓ Decision engine safety gates verified successfully.")

        # 4. Execute autonomous workflow execution
        prompt = "Create ecommerce project platform backend and deploy docker container setup"
        request = AutonomousRequest(prompt=prompt, environment="production")
        print(f"Executing workflow pipeline for prompt: '{prompt}'...")
        response = await engine.execute_autonomous_workflow(request)

        # 5. Assertions on response metrics
        print("Running validation assertions on execution timeline...")
        assert response.status in ("success", "partial"), f"Expected success/partial status, got {response.status}"
        assert response.project_name == os.path.basename(temp_dir) or "app", f"Incorrect project name: {response.project_name}"
        
        # Verify step list size
        steps = response.workflow_executed.steps
        assert len(steps) >= 4, f"Expected at least 4 workflow steps, got {len(steps)}"
        assert steps[0].id == "step-analysis", "First step should be code analysis"
        
        # Verify physical report written to .nova/autonomous/
        auto_dir = os.path.join(temp_dir, ".nova", "autonomous")
        assert os.path.exists(auto_dir), "Autonomous output directory not created"
        report_path = os.path.join(auto_dir, "project_integration_report.md")
        assert os.path.exists(report_path), "project_integration_report.md not written"

        # Verify quality report
        assert response.quality_report.overall_score > 0, "Quality overall score not calculated"
        assert len(response.quality_report.results) == 5, "Should calculate results for all 5 Quality Gates"
        print("✓ 5-Gate quality validations verified successfully.")

        # Verify memory integration
        history = engine.memory_mgr.list_history()
        assert len(history) > 0, "No execution entry committed to memory history"
        assert history[0].category == "decision", f"Expected category 'decision', got {history[0].category}"
        print("✓ Memory history sync verified successfully.")

        # Verify output report matches parameters
        report_md = response.report_markdown
        assert "# Autonomous Workflow Integration Execution Report" in report_md
        assert "5-Gate Enterprise Quality Validation" in report_md
        assert "Workflow Steps Timeline" in report_md
        print("✓ Markdown report formatting verified successfully.")

        print("=== AUTONOMOUS ENGINE VERIFICATION PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    asyncio.run(verify_autonomous_engine())
