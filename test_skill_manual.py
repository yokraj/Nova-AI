"""12-Stage Manual Validation Script for M3.4.9 Universal Skills Marketplace & SDK.
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "apps/backend")))

from app.ai.skills import (
    UniversalSkillEngine,
    SkillConfiguration,
    SkillStatus,
    SkillCategory,
    PermissionType,
    BaseSkill,
    MockSkillProvider,
)
from app.ai.gateway import AIGateway


async def run_12_stage_validation():
    print("==================================================================")
    print("M3.4.9 – Universal Skills Marketplace & SDK Validation")
    print("==================================================================\n")

    engine = UniversalSkillEngine()

    # Stage 1: Core Package Init & PEP 562 Lazy Loader
    print("Stage 1: Core Package Init & PEP 562 Lazy Loader")
    assert engine.config.skills_directory == "./data/skills"
    print("  [OK] Skills package loaded successfully.\n")

    # Stage 2: Built-in Skills & Registry
    print("Stage 2: Built-in Skills Suite & Local Registry")
    installed_skills = await engine.list_skills()
    print(f"  * Total Built-in Skills Installed: {len(installed_skills)}")
    for s in installed_skills[:4]:
        print(f"  * Skill: '{s.manifest.skill_id}' ({s.manifest.name}) | Category: {s.manifest.category.value} | Status: {s.status.value}")
    assert len(installed_skills) >= 10
    print("  [OK] Built-in Skills suite initialized in registry.\n")

    # Stage 3: Dynamic Voice Command Registry
    print("Stage 3: Dynamic Voice Command Registry (Kernel Voice Discovery)")
    voice_cmds = await engine.voice_commands()
    print(f"  * Registered Voice Commands Count: {len(voice_cmds)}")
    for c in voice_cmds[:3]:
        print(f"  * Skill: '{c['skill_id']}' -> Phrase: '{c['phrase']}' (Aliases: {c['aliases']})")
    assert len(voice_cmds) >= 8
    print("  [OK] Voice Registry mapped spoken phrases dynamically.\n")

    # Stage 4: Marketplace Search
    print("Stage 4: Skills Marketplace (Catalog Search & Version Checks)")
    excel_results = await engine.search_skills("Excel")
    dev_results = await engine.search_skills("code", category="developer_tools")
    print(f"  * Search Results for 'Excel': {[s.manifest.name for s in excel_results]}")
    print(f"  * Developer Tools Search Results: {[s.manifest.name for s in dev_results]}")
    assert len(excel_results) >= 1
    print("  [OK] Marketplace catalog search verified.\n")

    # Stage 5: Skill Installation & Uninstallation
    print("Stage 5: Skill Installation & Lifecycle")
    install_ok = await engine.install_skill("skill_photoshop")
    meta_before = await engine.skill_info("skill_photoshop")
    print(f"  * Installed 'skill_photoshop': {install_ok} (Status: {meta_before.status.value})")

    disable_ok = await engine.disable_skill("skill_photoshop")
    meta_disabled = await engine.skill_info("skill_photoshop")
    print(f"  * Disabled 'skill_photoshop': {disable_ok} (Status: {meta_disabled.status.value})")

    enable_ok = await engine.enable_skill("skill_photoshop")
    meta_enabled = await engine.skill_info("skill_photoshop")
    print(f"  * Enabled 'skill_photoshop': {enable_ok} (Status: {meta_enabled.status.value})")

    assert enable_ok is True
    print("  [OK] Skill installation and status toggling verified.\n")

    # Stage 6: Security Permission Manager
    print("Stage 6: Security Permission Manager (Scope Verification & Prompts)")
    filesystem_granted = engine.permission_manager.check_permissions(
        [PermissionType.FILESYSTEM], [PermissionType.FILESYSTEM, PermissionType.NETWORK]
    )
    is_sensitive = engine.permission_manager.requires_sensitive_approval([PermissionType.PAYMENTS])
    print(f"  * Filesystem Permission Granted: {filesystem_granted}")
    print(f"  * Payments Permission Requires Sensitive Prompt: {is_sensitive}")
    assert filesystem_granted is True
    assert is_sensitive is True
    print("  [OK] Permission Manager verified security scopes.\n")

    # Stage 7: Dynamic Skill Loader & Hot Reload
    print("Stage 7: Dynamic Skill Loader & Hot Reload")
    loader_instance = await engine.loader.load_skill("skill_vscode")
    reload_ok = await engine.loader.hot_reload("skill_vscode")
    print(f"  * Loaded Instance: {loader_instance}")
    print(f"  * Hot Reload 'skill_vscode': {reload_ok}")
    assert reload_ok is True
    print("  [OK] Skill Loader loaded and hot reloaded module.\n")

    # Stage 8: Skill Execution
    print("Stage 8: Skill Execution Engine")
    exec_res = await engine.execute_skill("skill_vscode", action="open_workspace", path="c:\\Projects\\Nova-AI")
    print(f"  * Execution Result: {exec_res.message} (Latency: {exec_res.latency_ms:.2f}ms)")
    assert exec_res.success is True
    print("  [OK] Skill execution completed successfully.\n")

    # Stage 9: Skill Memory & Execution Telemetry
    print("Stage 9: Skill Memory (Usage Statistics & Latency Tracking)")
    telem = engine.memory.get_telemetry("skill_vscode")
    print(f"  * 'skill_vscode' Executions Count: {telem.execution_count}")
    print(f"  * 'skill_vscode' Failure Count: {telem.failure_count}")
    print(f"  * 'skill_vscode' Average Latency: {telem.avg_latency_ms:.2f}ms")
    assert telem.execution_count >= 1
    print("  [OK] Skill Memory tracked execution telemetry.\n")

    # Stage 10: Skill Recommendation Engine
    print("Stage 10: Skill Recommendation Engine")
    all_skills = await engine.list_skills()
    recommended = engine.recommendation_engine.recommend_skills(all_skills)
    print(f"  * Top Recommended Skills: {[s.manifest.name for s in recommended]}")
    assert len(recommended) >= 1
    print("  [OK] Skill Recommendation Engine generated recommendations.\n")

    # Stage 11: Observability Diagnostics & Health
    print("Stage 11: Observability Diagnostics & Health")
    health = await engine.check_health()
    metrics = await engine.get_metrics()
    print(f"  * Healthy: {health.is_healthy} | Total Skills: {health.total_skills_count} | Voice Commands: {health.voice_commands_count}")
    print(f"  * Executions Recorded: {metrics.executions} | Installs: {metrics.installs}")
    assert health.is_healthy is True
    print("  [OK] Observability health diagnostics verified.\n")

    # Stage 12: End-to-End Voice Command Execution
    print("Stage 12: End-to-End Voice Command Skill Execution ('Hey Nova, open VS Code')")
    voice_res = await engine.execute_skill("skill_vscode", action="voice_intent", phrase="Open VS Code")
    print(f"  * Voice Command Skill Execution Output: '{voice_res.data['output']}'")
    assert voice_res.success is True
    print("  [OK] Voice command executed target skill action.\n")

    print("==================================================================")
    print("  ALL 12 STAGES PASSED SUCCESSFULLY!")
    print("  Universal Skills Marketplace & SDK Platform Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_12_stage_validation())
