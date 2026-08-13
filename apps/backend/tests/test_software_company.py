"""Unit and integration tests for M3.4.21 Autonomous AI Software Engineering Company & End-to-End Project Factory.
"""

import pytest
from app.ai.software_company.dashboard_runtime import SoftwareDashboardRuntime
from app.ai.software_company.divisions.architecture import SystemArchitectureDivision
from app.ai.software_company.divisions.backend import BackendDivision
from app.ai.software_company.divisions.code_review import CodeReviewDivision
from app.ai.software_company.divisions.database import DatabaseDivision
from app.ai.software_company.divisions.debugging import DebuggingDivision
from app.ai.software_company.divisions.devops import DevOpsDivision
from app.ai.software_company.divisions.documentation import DocumentationDivision
from app.ai.software_company.divisions.frontend import FrontendDivision
from app.ai.software_company.divisions.requirements import ProjectRequirementsDivision
from app.ai.software_company.divisions.testing import TestingDivision
from app.ai.software_company.engine import AutonomousSoftwareCompanyEngine
from app.ai.software_company.models import BuildStatus, ProjectStage
from app.ai.software_company.project_factory import ProjectFactoryEngine
from app.ai.software_company.project_memory import ContinuousProjectMemory
from app.ai.software_company.voice_software_company import VoiceSoftwareCompany


@pytest.mark.anyio
async def test_requirements_and_architecture_divisions():
    req_div = ProjectRequirementsDivision()
    spec = await req_div.extract_requirements("Build an ERP system")
    assert "erp" in spec.title.lower()
    assert len(spec.user_stories) >= 3

    arch_div = SystemArchitectureDivision()
    arch = await arch_div.design_architecture(spec)
    assert len(arch.components) >= 5
    assert len(arch.folder_structure) >= 5


@pytest.mark.anyio
async def test_backend_and_database_divisions():
    db_div = DatabaseDivision()
    spec = db_div.generate_database_schema(None)
    assert "users" in spec.tables

    backend_div = BackendDivision()
    endpoints = backend_div.build_backend()
    assert len(endpoints) == 4


@pytest.mark.anyio
async def test_testing_code_review_devops_divisions():
    testing_div = TestingDivision()
    test_res = testing_div.execute_test_suite()
    assert test_res["all_tests_passed"] is True
    assert test_res["coverage_percent"] >= 90.0

    review_div = CodeReviewDivision()
    review_res = review_div.review_pull_request()
    assert review_res["approved"] is True

    devops_div = DevOpsDivision()
    devops_res = devops_div.deploy_project()
    assert devops_res["container_status"] == "RUNNING"


@pytest.mark.anyio
async def test_project_factory_end_to_end():
    factory = ProjectFactoryEngine()
    build_res = await factory.build_project("Build a Hospital Management System")
    assert build_res.status == BuildStatus.SUCCESS
    assert build_res.stage == ProjectStage.DELIVERED
    assert build_res.generated_files_count >= 15


@pytest.mark.anyio
async def test_continuous_project_memory_and_dashboard():
    memory = ContinuousProjectMemory()
    item = memory.store_memory("proj_01", "architecture", {"pattern": "Microservices"})
    assert item.category == "architecture"

    retrieved = memory.get_project_history("proj_01")
    assert len(retrieved) == 1

    dash = SoftwareDashboardRuntime()
    status = dash.get_dashboard_status()
    assert status.build_status == BuildStatus.SUCCESS


@pytest.mark.anyio
async def test_autonomous_software_company_engine_master_facade():
    engine = AutonomousSoftwareCompanyEngine()
    build_res = await engine.build_software("Build an ERP system with FastAPI and React")
    assert build_res.status == BuildStatus.SUCCESS

    voice_res = await engine.process_voice_build_command("Hey Nova, build an ERP system")
    assert voice_res["status"] == BuildStatus.SUCCESS.value

    health = engine.get_company_health()
    assert health.is_healthy is True
    assert health.engineering_divisions_count == 13
