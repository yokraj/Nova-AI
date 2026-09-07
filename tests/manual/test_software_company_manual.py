"""20-Stage Comprehensive Manual Validation Script for M3.4.21 Autonomous AI Software Engineering Company & End-to-End Project Factory.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps/backend")))


async def run_20_stage_validation():
    print("==================================================================")
    print("M3.4.21 – Autonomous AI Software Engineering Company & End-to-End Factory")
    print("==================================================================\n")

    # Stage 1: Software Company Package Init & PEP 562 Lazy Loader
    print("Stage 1: Software Company Package Init & PEP 562 Lazy Loader")
    from app.ai.software_company import SoftwareCompanyConfiguration, AutonomousSoftwareCompanyEngine
    config = SoftwareCompanyConfiguration()
    print(f"  * Company Name: '{config.company_name}' v{config.version} | Local-First = {config.local_first}")
    assert config.enabled is True
    print("  [OK] Software Company package init & lazy loader verified.\n")

    # Stage 2: Central Software Company Engine Facade & Health Diagnostic
    print("Stage 2: Central Software Company Engine Facade & Health Diagnostic")
    engine = AutonomousSoftwareCompanyEngine()
    health = engine.get_company_health()
    print(f"  * Company Health: Status = '{health.status}' | Divisions = {health.engineering_divisions_count} | Factory Active = {health.project_factory_active}")
    assert health.is_healthy is True and health.engineering_divisions_count == 13
    print("  [OK] Central Software Company Engine facade verified.\n")

    # Stage 3: Phase 1 Project Requirements Division
    print("Stage 3: Phase 1 Project Requirements Division")
    from app.ai.software_company.divisions.requirements import ProjectRequirementsDivision
    req_div = ProjectRequirementsDivision()
    spec = await req_div.extract_requirements("Build a Hospital Management System")
    print(f"  * Project Title: '{spec.title}' | User Stories ({len(spec.user_stories)}): {spec.user_stories[0]}")
    assert "Hospital" in spec.title and len(spec.user_stories) >= 3
    print("  [OK] Project Requirements Division verified.\n")

    # Stage 4: Phase 2 System Architecture Division
    print("Stage 4: Phase 2 System Architecture Division")
    from app.ai.software_company.divisions.architecture import SystemArchitectureDivision
    arch_div = SystemArchitectureDivision()
    arch = await arch_div.design_architecture(spec)
    print(f"  * Blueprint Components ({len(arch.components)}): {arch.components[:3]}")
    print(f"  * Folder Structure Count: {len(arch.folder_structure)} | Deployment Topology = '{arch.deployment_topology}'")
    assert len(arch.components) >= 5
    print("  [OK] System Architecture Division verified.\n")

    # Stage 5: Phase 3 UI / UX Division
    print("Stage 5: Phase 3 UI / UX Division")
    from app.ai.software_company.divisions.uiux import UIUXDivision
    uiux_div = UIUXDivision()
    ui_design = uiux_div.design_interface(spec.title)
    print(f"  * Design System: '{ui_design['design_system']}' | Palette: {ui_design['color_palette']}")
    assert ui_design["components_count"] >= 10
    print("  [OK] UI / UX Division verified.\n")

    # Stage 6: Phase 4 Database Division
    print("Stage 6: Phase 4 Database Division")
    from app.ai.software_company.divisions.database import DatabaseDivision
    db_div = DatabaseDivision()
    db_schema = db_div.generate_database_schema(spec)
    print(f"  * Database Tables ({len(db_schema.tables)}): {db_schema.tables} | Migrations = {db_schema.migration_scripts}")
    assert "users" in db_schema.tables
    print("  [OK] Database Division verified.\n")

    # Stage 7: Phase 5 Backend Division
    print("Stage 7: Phase 5 Backend Division")
    from app.ai.software_company.divisions.backend import BackendDivision
    backend_div = BackendDivision()
    endpoints = backend_div.build_backend()
    print(f"  * Generated REST API Endpoints ({len(endpoints)}): First = '{endpoints[0].method} {endpoints[0].path}'")
    assert len(endpoints) == 4
    print("  [OK] Backend Division verified.\n")

    # Stage 8: Phase 6 Frontend Division
    print("Stage 8: Phase 6 Frontend Division")
    from app.ai.software_company.divisions.frontend import FrontendDivision
    frontend_div = FrontendDivision()
    frontend_res = frontend_div.build_frontend()
    print(f"  * Frontend Stack: '{frontend_res['framework']}' | Generated Components = {frontend_res['generated_components_count']}")
    assert frontend_res["generated_components_count"] >= 15
    print("  [OK] Frontend Division verified.\n")

    # Stage 9: Phase 7 Mobile Division
    print("Stage 9: Phase 7 Mobile Division")
    from app.ai.software_company.divisions.mobile import MobileDivision
    mobile_div = MobileDivision()
    mobile_res = mobile_div.build_mobile_app()
    print(f"  * Mobile App Framework: '{mobile_res['mobile_framework']}' | Platforms: {mobile_res['platforms']}")
    assert "Android" in mobile_res["platforms"]
    print("  [OK] Mobile Division verified.\n")

    # Stage 10: Phase 8 Testing Division (Unit, Integration & E2E Test Suite)
    print("Stage 10: Phase 8 Testing Division (Unit, Integration & E2E Test Suite)")
    from app.ai.software_company.divisions.testing import TestingDivision
    testing_div = TestingDivision()
    test_res = testing_div.execute_test_suite()
    print(f"  * Unit Tests Passed: {test_res['unit_tests_passed']} | Test Coverage = {test_res['coverage_percent']}%")
    assert test_res["all_tests_passed"] is True
    print("  [OK] Testing Division verified.\n")

    # Stage 11: Phase 9 Code Review Division (Architecture, Security, QA Review)
    print("Stage 11: Phase 9 Code Review Division (Architecture, Security, QA Review)")
    from app.ai.software_company.divisions.code_review import CodeReviewDivision
    review_div = CodeReviewDivision()
    review_res = review_div.review_pull_request()
    print(f"  * PR Review Status: '{review_res['merge_status']}' | Score = {review_res['quality_score']} | Vulnerabilities = {review_res['security_vulnerabilities_found']}")
    assert review_res["approved"] is True
    print("  [OK] Code Review Division verified.\n")

    # Stage 12: Phase 10 Debugging Division & Automated Bug Fixing
    print("Stage 12: Phase 10 Debugging Division & Automated Bug Fixing")
    from app.ai.software_company.divisions.debugging import DebuggingDivision
    debugging_div = DebuggingDivision()
    autofix_res = debugging_div.autofix_bugs("IndexError: list index out of range in auth middleware")
    print(f"  * Bugs Fixed: {autofix_res['bugs_detected']} | Root Cause = '{autofix_res['root_cause']}' | Patch Applied = {autofix_res['autofix_patch_applied']}")
    assert autofix_res["retest_passed"] is True
    print("  [OK] Debugging Division verified.\n")

    # Stage 13: Phase 11 DevOps Division (Docker, Compose & CI/CD)
    print("Stage 13: Phase 11 DevOps Division (Docker, Compose & CI/CD)")
    from app.ai.software_company.divisions.devops import DevOpsDivision
    devops_div = DevOpsDivision()
    devops_res = devops_div.deploy_project()
    print(f"  * Docker Deployment: Status = '{devops_res['container_status']}' | URL = '{devops_res['health_check_url']}'")
    assert devops_res["container_status"] == "RUNNING"
    print("  [OK] DevOps Division verified.\n")

    # Stage 14: Phase 12 Documentation Division (OpenAPI & Developer Guides)
    print("Stage 14: Phase 12 Documentation Division (OpenAPI & Developer Guides)")
    from app.ai.software_company.divisions.documentation import DocumentationDivision
    doc_div = DocumentationDivision()
    doc_res = doc_div.generate_documentation(spec.title)
    print(f"  * Documentation Generated: README = {doc_res['readme_generated']} | Developer Guide = '{doc_res['developer_guide']}'")
    assert doc_res["readme_generated"] is True
    print("  [OK] Documentation Division verified.\n")

    # Stage 15: Phase 13 Project Management Division (Sprint & Roadmap)
    print("Stage 15: Phase 13 Project Management Division (Sprint & Roadmap)")
    from app.ai.software_company.divisions.project_management import ProjectManagementDivision
    pm_div = ProjectManagementDivision()
    pm_res = pm_div.create_sprint_plan()
    print(f"  * Current Sprint: '{pm_res['current_sprint']}' | Assigned Tasks = {pm_res['tasks_assigned_count']}")
    assert pm_res["tasks_assigned_count"] >= 10
    print("  [OK] Project Management Division verified.\n")

    # Stage 16: Phase 14 Autonomous Project Factory End-to-End Pipeline
    print("Stage 16: Phase 14 Autonomous Project Factory End-to-End Pipeline")
    from app.ai.software_company.project_factory import ProjectFactoryEngine
    factory = ProjectFactoryEngine()
    build_result = await factory.build_project("Build an ERP system using FastAPI, React and PostgreSQL")
    print(f"  * Factory Project Output: '{build_result.title}' | Status = '{build_result.status.value}' | Stage = '{build_result.stage.value}'")
    print(f"  * Generated Files = {build_result.generated_files_count} | Test Coverage = {build_result.test_coverage_percent}% | URL = '{build_result.deployment_url}'")
    assert build_result.status.value == "SUCCESS"
    print("  [OK] Autonomous Project Factory verified.\n")

    # Stage 17: Phase 15 Continuous Project Memory
    print("Stage 17: Phase 15 Continuous Project Memory")
    from app.ai.software_company.project_memory import ContinuousProjectMemory
    memory = ContinuousProjectMemory()
    mem_item = memory.store_memory(build_result.project_id, "architecture_decision", {"database": "PostgreSQL", "orm": "SQLAlchemy V2"})
    history = memory.get_project_history(build_result.project_id)
    print(f"  * Memory Retained: Category = '{mem_item.category}' | Total Project History Items = {len(history)}")
    assert len(history) == 1
    print("  [OK] Continuous Project Memory verified.\n")

    # Stage 18: Phase 16 Voice-Driven Software Company ("Hey Nova, build an ERP")
    print("Stage 18: Phase 16 Voice-Driven Software Company ('Hey Nova, build an ERP')")
    from app.ai.software_company.voice_software_company import VoiceSoftwareCompany
    voice_company = VoiceSoftwareCompany(factory)
    voice_build_res = await voice_company.process_voice_project_request("Hey Nova, build an ERP system using FastAPI and React")
    print(f"  * Voice Request Processed: Title = '{voice_build_res['title']}' | Status = '{voice_build_res['status']}'")
    assert voice_build_res["status"] == "SUCCESS"
    print("  [OK] Voice-Driven Software Company verified.\n")

    # Stage 19: Phase 17 Project Dashboard & Software Analytics Runtime
    print("Stage 19: Phase 17 Project Dashboard & Software Analytics Runtime")
    from app.ai.software_company.dashboard_runtime import SoftwareDashboardRuntime
    dashboard = SoftwareDashboardRuntime()
    dash_status = dashboard.get_dashboard_status()
    print(f"  * Dashboard Company: '{dash_status.company_name}' | Coverage = {dash_status.test_coverage_percent}% | Bugs Fixed = {dash_status.bugs_fixed_count}")
    assert dash_status.build_status.value == "SUCCESS"
    print("  [OK] Project Dashboard Runtime verified.\n")

    # Stage 20: System Integration & Master Health Verification
    print("Stage 20: System Integration & Master Health Verification")
    master_health = engine.get_company_health()
    print(f"  * Master Company Health: Status = '{master_health.status}' | Registered Agents = {master_health.total_factory_agents}")
    assert master_health.is_healthy is True and master_health.engineering_divisions_count == 13
    print("  [OK] System Integration & Master Health Verification complete.\n")

    print("==================================================================")
    print("  ALL 20 STAGES PASSED SUCCESSFULLY!")
    print("  Autonomous AI Software Engineering Company & Factory Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_20_stage_validation())
