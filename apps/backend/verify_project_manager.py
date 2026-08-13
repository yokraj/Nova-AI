"""Verification script for the Enterprise Software Project Manager Engine.
"""

import os
import asyncio
import tempfile
from app.agents.software_engineer.project_manager.engine import LocalProjectManagerEngine

async def verify_project_manager():
    print("=== STARTING PROJECT MANAGER ENGINE VERIFICATION ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Creating sandbox project directory in: {temp_dir}")

        # 1. Instantiate engine
        engine = LocalProjectManagerEngine(gateway=None, workspace_root=temp_dir)

        # 2. Process requirements
        prompt = "Create an ecommerce platform with secure payment checkout"
        print(f"Processing project requirements prompt: '{prompt}'...")
        report = await engine.process_requirements(prompt)

        # 3. Assertions and validations
        print("Running validation assertions...")

        # Validate Report output
        assert report.status == "success", f"Expected success status, got {report.status}"
        assert report.project_name == "Ecommerce System", f"Expected Ecommerce System, got {report.project_name}"
        assert report.format_type == "markdown", f"Expected markdown, got {report.format_type}"
        assert len(report.content_markdown) > 0, "Expected non-empty report markdown"

        # Validate physical files written to .nova/project_manager/
        pm_dir = os.path.join(temp_dir, ".nova", "project_manager")
        assert os.path.exists(pm_dir), "Project manager output directory not created"
        
        report_path = os.path.join(pm_dir, "project_report.md")
        timeline_path = os.path.join(pm_dir, "timeline.md")
        sync_path = os.path.join(pm_dir, "dev_sync.txt")

        assert os.path.exists(report_path), "project_report.md not written"
        assert os.path.exists(timeline_path), "timeline.md not written"
        assert os.path.exists(sync_path), "dev_sync.txt not written"

        # Validate cache variables
        assert engine.cache.get("last_project_name") == "Ecommerce System"
        assert engine.cache.get("last_project_hash") is not None

        # Verify parsed contents from report
        markdown = report.content_markdown
        assert "# Project Management Report: Ecommerce System" in markdown, "Missing project title in report"
        assert "Authentication" in markdown, "Missing Authentication module in report"
        assert "Payment" in markdown, "Missing Payment module in report"
        assert "Remaining Work Hours" in markdown, "Missing Remaining Work Hours progress metric"
        assert "Risk Assessment Mitigation Plans" in markdown, "Missing Risk assessment section"

        print("✓ All validation assertions passed successfully.")
        print("=== PROJECT MANAGER ENGINE VERIFICATION PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    asyncio.run(verify_project_manager())
