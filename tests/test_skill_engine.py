"""Unit and integration tests for Universal Skills Marketplace & SDK.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/backend")))

from app.ai.skills.skill_engine import UniversalSkillEngine
from app.ai.skills.mock_provider import MockSkillProvider
from app.ai.skills.models import (
    PermissionType,
    SkillCategory,
    SkillStatus,
)


@pytest.mark.anyio
async def test_builtin_skills_initialization():
    engine = UniversalSkillEngine()
    skills = await engine.list_skills()
    assert len(skills) >= 12
    skill_ids = [s.manifest.skill_id for s in skills]
    assert "skill_vscode" in skill_ids
    assert "skill_git" in skill_ids
    assert "skill_excel" in skill_ids
    assert "skill_chrome" in skill_ids


@pytest.mark.anyio
async def test_voice_command_registry():
    engine = UniversalSkillEngine()
    cmds = await engine.voice_commands()
    assert len(cmds) >= 10
    phrases = [c["phrase"] for c in cmds]
    assert "Open VS Code" in phrases
    assert "Open Chrome" in phrases


@pytest.mark.anyio
async def test_marketplace_search_and_installation():
    engine = UniversalSkillEngine()
    results = await engine.search_skills("Excel")
    assert len(results) >= 1
    assert "Excel" in results[0].manifest.name

    installed = await engine.install_skill("skill_photoshop")
    assert installed is True
    meta = await engine.skill_info("skill_photoshop")
    assert meta is not None
    assert meta.status == SkillStatus.ENABLED or meta.status == SkillStatus.INSTALLED


@pytest.mark.anyio
async def test_enable_disable_skill():
    engine = UniversalSkillEngine()
    disabled = await engine.disable_skill("skill_vscode")
    assert disabled is True
    meta = await engine.skill_info("skill_vscode")
    assert meta.status == SkillStatus.DISABLED

    enabled = await engine.enable_skill("skill_vscode")
    assert enabled is True
    meta2 = await engine.skill_info("skill_vscode")
    assert meta2.status == SkillStatus.ENABLED


@pytest.mark.anyio
async def test_permission_manager():
    engine = UniversalSkillEngine()
    has_perm = engine.permission_manager.check_permissions([PermissionType.FILESYSTEM], [PermissionType.FILESYSTEM, PermissionType.NETWORK])
    assert has_perm is True

    sensitive = engine.permission_manager.requires_sensitive_approval([PermissionType.PAYMENTS])
    assert sensitive is True


@pytest.mark.anyio
async def test_skill_execution_and_memory():
    engine = UniversalSkillEngine()
    res = await engine.execute_skill("skill_vscode", action="open_file", file_path="main.py")
    assert res.success is True
    assert "skill_vscode" in res.skill_id

    telem = engine.memory.get_telemetry("skill_vscode")
    assert telem.execution_count >= 1


@pytest.mark.anyio
async def test_skill_recommendations():
    engine = UniversalSkillEngine()
    skills = await engine.list_skills()
    recommended = engine.recommendation_engine.recommend_skills(skills)
    assert len(recommended) >= 1


@pytest.mark.anyio
async def test_skill_health_and_metrics():
    engine = UniversalSkillEngine()
    await engine.execute_skill("skill_chrome", action="navigate")

    health = await engine.check_health()
    assert health.is_healthy is True
    assert health.total_skills_count >= 12

    metrics = await engine.get_metrics()
    assert metrics.executions >= 1


@pytest.mark.anyio
async def test_mock_skill_provider():
    mock = MockSkillProvider()
    skills = await mock.mock_list_skills()
    assert len(skills) == 1
    res = await mock.mock_execute("test_skill")
    assert res.success is True
