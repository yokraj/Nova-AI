"""12-Stage Manual Validation Script for M3.4.3 AI Software Copilot.
"""

import asyncio
import os
import sys

# Ensure UTF-8 output encoding for Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add apps/backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps/backend")))

from app.ai.copilot import (
    CopilotEngine,
    CopilotConfiguration,
    CopilotState,
    ProjectLanguage,
    ArchitectureStyle,
    SDLCStage,
    MockCopilotProvider,
)
from app.ai.gateway import AIGateway, ProviderRegistry, ModelRegistry, ProviderFactory, RetryPolicy, TimeoutPolicy


async def run_12_stage_validation():
    print("==================================================================")
    print("M3.4.3 – AI Software Copilot Professional Engine Validation")
    print("==================================================================\n")

    engine = CopilotEngine()

    # Stage 1: Core Copilot Init & PEP 562 Lazy Loader
    print("Stage 1: Core Copilot Package Init & PEP 562 Lazy Loader")
    assert engine.config.default_language == "python"
    print("  [OK] Copilot package loaded successfully.\n")

    # Stage 2: Requirement Analysis Engine
    print("Stage 2: Requirement Analysis Engine (Prompt -> RequirementDocument)")
    reqs = await engine.requirement_analyzer.analyze_requirements("Build an Enterprise ERP system with FastAPI, React, and PostgreSQL")
    print(f"  * Project Name: {reqs.project_name}")
    print(f"  * Business Goals: {reqs.business_goals[0]}")
    print(f"  * Functional Reqs Count: {len(reqs.functional_requirements)}")
    print(f"  * Tech Preferences: {reqs.technology_preferences}")
    assert len(reqs.functional_requirements) > 0
    print("  [OK] Requirement Analysis Engine extracted structured specifications.\n")

    # Stage 3: Software Architecture Engine
    print("Stage 3: Software Architecture Engine (System Architecture & Boundaries)")
    arch = await engine.architecture_engine.design_architecture(reqs)
    print(f"  * Style: {arch.style.value}")
    print(f"  * Service Boundaries: {arch.service_boundaries[:3]}")
    print(f"  * Auth Strategy: {arch.auth_strategy}")
    assert arch.style == ArchitectureStyle.MODULAR_MONOLITH
    print("  [OK] Software Architecture Engine generated system design.\n")

    # Stage 4: Technology Selection Engine
    print("Stage 4: Technology Selection Engine (Stack Selection)")
    stack = await engine.technology_selector.select_technologies(reqs, arch)
    print(f"  * Languages: {stack.languages}")
    print(f"  * Frameworks: {stack.frameworks}")
    print(f"  * Databases: {stack.databases}")
    assert "python" in stack.languages
    print("  [OK] Technology Selection Engine resolved technology stack.\n")

    # Stage 5: Code Generation Engine
    print("Stage 5: Code Generation Engine (Multi-File Code Generation)")
    files = await engine.code_generator.generate_code(reqs, arch, stack)
    print(f"  * Generated Files Count: {len(files)}")
    for f in files:
        print(f"    - {f.path} ({f.language}, {f.file_type})")
    assert len(files) >= 5
    print("  [OK] Code Generation Engine produced backend, frontend, tests, and config.\n")

    # Stage 6: Code Understanding Engine
    print("Stage 6: Code Understanding Engine (Repo Analysis & Diagramming)")
    repo_info = await engine.analyze_project("c:\\Projects\\Nova-AI")
    print(f"  * Architecture Pattern: {repo_info['architecture_pattern']}")
    print(f"  * Entry Points: {repo_info['entry_points']}")
    print(f"  * Diagram:\n{repo_info['architecture_diagram']}")
    assert repo_info["architecture_pattern"] == "Modular Monolith"
    print("  [OK] Code Understanding Engine analyzed codebase architecture.\n")

    # Stage 7: Debugging Engine
    print("Stage 7: Debugging Engine (Automated Bug Fixing & Patching)")
    bug = await engine.debug_project("apps/backend/main.py", "KeyError: 'user_id'")
    print(f"  * Title: {bug.title}")
    print(f"  * Root Cause: {bug.root_cause}")
    print(f"  * Fix Verified: {bug.verified}")
    assert bug.verified is True
    print("  [OK] Debugging Engine isolated root cause and verified patch.\n")

    # Stage 8: Refactoring Engine
    print("Stage 8: Refactoring Engine (Code Optimization & Modernization)")
    ref = await engine.refactor_project("apps/backend/main.py", "Optimize data structures")
    print(f"  * Refactor Goal: {ref.refactor_goal}")
    print(f"  * Performance Impact: {ref.performance_impact}")
    assert ref.target_file == "apps/backend/main.py"
    print("  [OK] Refactoring Engine produced architectural optimization plan.\n")

    # Stage 9: Test Engineering Engine
    print("Stage 9: Test Engineering Engine (Automated Suite Execution)")
    tst = await engine.test_project("c:\\Projects\\Nova-AI")
    print(f"  * Total Tests: {tst.total_tests} | Passed: {tst.passed_tests}")
    print(f"  * Code Coverage: {tst.coverage_percent:.1f}%")
    assert tst.coverage_percent > 90.0
    print("  [OK] Test Engineering Engine executed test suites and coverage reports.\n")

    # Stage 10: DevOps Deployment Engine
    print("Stage 10: DevOps Deployment Engine (Docker & CI/CD Pipelines)")
    cfg = await engine.deploy_project("c:\\Projects\\Nova-AI")
    print(f"  * Target: {cfg.target}")
    print(f"  * CI/CD Provider: {cfg.ci_cd_pipeline['provider']}")
    print(f"  * Rollback Plan: {cfg.rollback_plan[:50]}...")
    assert cfg.target == "local_docker_compose"
    print("  [OK] DevOps Engine generated container and deployment specs.\n")

    # Stage 11: Documentation & Review Engines
    print("Stage 11: Documentation & Code Review Engines")
    rev = await engine.review_project("c:\\Projects\\Nova-AI")
    docs = await engine.document_project("NovaProject")
    print(f"  * Code Review Score: {rev.score:.1f}/100")
    print(f"  * Documentation Sections: README ({len(docs.readme_md)} bytes), API Docs ({len(docs.api_docs)} bytes)")
    assert rev.score >= 90.0
    print("  [OK] Documentation & Review Engines generated complete report suite.\n")

    # Stage 12: Voice-First Full SDLC Execution Pipeline
    print("Stage 12: Voice-First Full SDLC Project Creation ('Hey Nova, build an ERP')")
    project_state = await engine.create_project("Build a complete ERP system", name="VoiceERP")
    print(f"  * Project ID: {project_state.project_id}")
    print(f"  * SDLC Stage: {project_state.stage.value}")
    print(f"  * Total Files Created: {len(project_state.files)}")
    assert project_state.stage == SDLCStage.COMPLETED
    print("  [OK] Full SDLC project completed successfully via voice copilot engine.\n")

    print("==================================================================")
    print("  ALL 12 STAGES PASSED SUCCESSFULLY!")
    print("  AI Software Copilot Professional Engine Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_12_stage_validation())
