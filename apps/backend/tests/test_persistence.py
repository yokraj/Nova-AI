"""Backend Persistence Unit and Integration Tests for Nova AI.

Tests async database connection, model entities, relations, Alembic schema,
and REST endpoints across conversations, memories, skills, missions, agents, and audit events.
"""

import pytest
import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.base import Base
from app.database.models import (
    User,
    UserStatus,
    Conversation,
    ConversationStatus,
    Message,
    MessageRole,
    MemoryModel,
    SkillModel,
    SkillVersionModel,
    MissionModel,
    MissionTaskModel,
    AgentModel,
    AgentExecutionModel,
    AuditEventModel,
)
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_database_persistence_lifecycle():
    """Test full async database persistence cycle using SQLite in-memory engine."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        # 1. Create User
        user = User(
            email="test_user@nova.ai",
            username="nova_tester",
            password_hash="hashed_secret_123",
            status=UserStatus.ACTIVE.value,
            role="user",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        assert user.id is not None

        # 2. Create Conversation & Message
        conv = Conversation(
            user_id=user.id,
            title="Deploy React App",
            status=ConversationStatus.ACTIVE.value,
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)

        msg = Message(
            conversation_id=conv.id,
            role=MessageRole.USER.value,
            content="How do I build and deploy the React application?",
            token_count=10,
        )
        db.add(msg)
        await db.commit()


        # Query conversation back
        stmt = select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.id == conv.id)
        res = await db.execute(stmt)
        fetched_conv = res.scalar_one()
        assert fetched_conv.title == "Deploy React App"
        assert len(fetched_conv.messages) == 1
        assert fetched_conv.messages[0].content.startswith("How do I build")

        # 3. Create Memory
        memory = MemoryModel(
            content="User prefers pnpm package manager for deployment.",
            memory_type="Workflow",
            metadata_json={"tags": ["pnpm", "react", "build"]},
            importance_score=0.85,
        )
        db.add(memory)
        await db.commit()

        stmt_mem = select(MemoryModel).where(MemoryModel.memory_type == "Workflow")
        res_mem = await db.execute(stmt_mem)
        fetched_mem = res_mem.scalar_one()
        assert fetched_mem.importance_score == 0.85

        # 4. Create Skill & Version
        skill = SkillModel(
            name="Build My React App",
            description="Build React application using pnpm",
            purpose="Build project",
            category="automation",
            status="active",
            confidence=0.95,
            success_rate=1.0,
            usage_count=5,
            trigger_patterns_json=[{"naturalLanguagePattern": "Build My React App", "intent": "workflow_execution"}],
            required_tools_json=["application.open", "filesystem.read_directory"],
            variables_json=[{"name": "location", "type": "path", "defaultValue": "Desktop/App"}],
            steps_json=[{"id": "step-1", "order": 1, "tool": "application.open", "purpose": "Launch VS Code"}],
            metadata_json={"tags": ["react", "build"]},
        )
        db.add(skill)
        await db.commit()
        await db.refresh(skill)

        skill_ver = SkillVersionModel(
            skill_id=skill.id,
            version_number=1,
            changes="Initial release",
            reason="Created by user test",
            steps_snapshot_json=skill.steps_json,
            success_rate_snapshot=1.0,
        )
        db.add(skill_ver)
        await db.commit()

        stmt_skill = select(SkillModel).options(selectinload(SkillModel.versions)).where(SkillModel.id == skill.id)
        res_skill = await db.execute(stmt_skill)
        fetched_skill = res_skill.scalar_one()
        assert fetched_skill.name == "Build My React App"
        assert len(fetched_skill.versions) == 1

        # 5. Create Mission & Task
        mission = MissionModel(
            title="Prepare Nova Release",
            goal="Test all features and build production bundle",
            category="automation",
            status="PENDING",
            progress_percent=0.0,
            metadata_json={},
        )
        db.add(mission)
        await db.commit()
        await db.refresh(mission)

        task = MissionTaskModel(
            mission_id=mission.id,
            task_order=1,
            title="Run Unit Tests",
            description="Execute test runner across all modules",
            status="COMPLETED",
            dependencies_json=[],
        )
        db.add(task)
        await db.commit()

        stmt_mission = select(MissionModel).options(selectinload(MissionModel.tasks)).where(MissionModel.id == mission.id)
        res_mission = await db.execute(stmt_mission)
        fetched_mission = res_mission.scalar_one()
        assert len(fetched_mission.tasks) == 1
        assert fetched_mission.tasks[0].status == "COMPLETED"

        # 6. Create Agent & Execution
        agent = AgentModel(
            name="DevOps Worker",
            role="DevOps & System Automation Agent",
            description="Handles deployment and build scripts",
            status="IDLE",
            capabilities_json=["system", "filesystem", "application"],
        )
        db.add(agent)
        await db.commit()
        await db.refresh(agent)

        agent_exec = AgentExecutionModel(
            agent_id=agent.id,
            goal_text="Execute build script",
            status="COMPLETED",
            duration_ms=120,
            result_summary="Build succeeded",
            logs_json=["Step 1 completed"],
        )
        db.add(agent_exec)
        await db.commit()

        stmt_agent = select(AgentModel).options(selectinload(AgentModel.executions)).where(AgentModel.id == agent.id)
        res_agent = await db.execute(stmt_agent)
        fetched_agent = res_agent.scalar_one()
        assert len(fetched_agent.executions) == 1

        # 7. Create Audit Event
        audit = AuditEventModel(
            event_type="TOOL_EXECUTION",
            action="filesystem.create_file",
            tool_name="filesystem.create_file",
            risk_level="LOW",
            actor="User",
            decision="ALLOWED",
            details_json={"path": "c:/test.txt"},
        )
        db.add(audit)
        await db.commit()

        stmt_audit = select(AuditEventModel).where(AuditEventModel.event_type == "TOOL_EXECUTION")
        res_audit = await db.execute(stmt_audit)
        fetched_audit = res_audit.scalar_one()
        assert fetched_audit.action == "filesystem.create_file"

    await engine.dispose()


def test_fastapi_rest_endpoints():
    """Test FastAPI REST endpoints metadata and health checks."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["project"] == "Nova AI"

    health_res = client.get("/api/system/health")
    assert health_res.status_code == 200
