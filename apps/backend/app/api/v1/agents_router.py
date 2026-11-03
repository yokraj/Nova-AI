"""FastAPI REST router for Agent Workforce Management.
"""

from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.database.models.agent_model import AgentModel, AgentExecutionModel

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentCreateSchema(BaseModel):
    name: str
    role: str
    description: str
    status: str = "IDLE"
    capabilities: List[str] = Field(default_factory=list)


class AgentExecutionRequest(BaseModel):
    goal: str
    is_user_approved: bool = False
    time_budget_sec: float = 60.0


def format_agent(agent: AgentModel) -> dict:
    return {
        "id": str(agent.id),
        "name": agent.name,
        "role": agent.role,
        "description": agent.description,
        "status": agent.status,
        "capabilities": agent.capabilities_json or [],
        "performanceScore": agent.performance_score,
        "tasksCompleted": agent.tasks_completed,
        "createdAt": agent.created_at.isoformat() if agent.created_at else "",
        "updatedAt": agent.updated_at.isoformat() if agent.updated_at else "",
    }


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_agent(
    payload: AgentCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    agent = AgentModel(
        name=payload.name,
        role=payload.role,
        description=payload.description,
        status=payload.status,
        capabilities_json=payload.capabilities,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return format_agent(agent)


@router.get("", response_model=List[dict])
async def list_agents(db: AsyncSession = Depends(get_db)):
    stmt = select(AgentModel)
    result = await db.execute(stmt)
    agents = result.scalars().all()
    return [format_agent(a) for a in agents]


@router.get("/{agent_id}", response_model=dict)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    try:
        u_id = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID UUID format.")

    stmt = select(AgentModel).where(AgentModel.id == u_id)
    result = await db.execute(stmt)
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found.")

    return format_agent(agent)


@router.post("/execute", response_model=dict)
async def execute_agent_task(
    payload: AgentExecutionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Executes a natural language user goal using the Unified Agent Execution Engine."""
    from app.intelligence.agent_execution_engine import AgentExecutionEngine
    engine = AgentExecutionEngine()
    analysis = engine.understand_task(payload.goal)
    plan = engine.create_plan(payload.goal, analysis)
    report = await engine.execute_plan(
        plan,
        time_budget_sec=payload.time_budget_sec,
        is_user_approved=payload.is_user_approved,
    )
    return report.to_dict()
