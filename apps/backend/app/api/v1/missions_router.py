"""FastAPI REST router for Mission, Task, Checkpoint, Approval & Recovery Management.
"""

from typing import List, Optional, Any
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.database.models.mission_model import MissionModel, MissionTaskModel
from app.database.models.mission_checkpoint_model import (
    MissionCheckpointModel,
    MissionApprovalModel,
    MissionRecoveryEventModel,
)

router = APIRouter(prefix="/missions", tags=["missions"])


class TaskCreateSchema(BaseModel):
    taskOrder: int = 1
    title: str
    description: str
    status: str = "PENDING"
    assignedAgent: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)


class MissionCreateSchema(BaseModel):
    title: str
    goal: str
    category: str = "automation"
    status: str = "PENDING"
    assignedAgent: Optional[str] = None
    tasks: List[TaskCreateSchema] = Field(default_factory=list)


class CheckpointCreateSchema(BaseModel):
    executionId: str
    checkpointId: str
    status: str = "EXECUTING"
    currentStep: int = 0
    completedSteps: List[Any] = Field(default_factory=list)
    pendingSteps: List[Any] = Field(default_factory=list)
    retryCounters: dict = Field(default_factory=dict)
    budgetState: dict = Field(default_factory=dict)
    approvalState: dict = Field(default_factory=dict)
    verificationResults: List[Any] = Field(default_factory=list)
    checkpointVersion: int = 1
    isSafeResumable: bool = True


class ApprovalActionSchema(BaseModel):
    approved: bool
    authorizedBy: str = "Operator"


def format_mission(mission: MissionModel) -> dict:
    return {
        "id": str(mission.id),
        "title": mission.title,
        "goal": mission.goal,
        "category": mission.category,
        "status": mission.status,
        "progressPercent": mission.progress_percent,
        "assignedAgent": mission.assigned_agent,
        "createdAt": mission.created_at.isoformat() if mission.created_at else "",
        "updatedAt": mission.updated_at.isoformat() if mission.updated_at else "",
        "tasks": [
            {
                "id": str(t.id),
                "taskOrder": t.task_order,
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "assignedAgent": t.assigned_agent,
                "dependencies": t.dependencies_json or [],
                "outputSummary": t.output_summary,
            }
            for t in (mission.tasks or [])
        ],
    }


def format_checkpoint(cp: MissionCheckpointModel) -> dict:
    return {
        "id": str(cp.id),
        "missionId": str(cp.mission_id),
        "executionId": cp.execution_id,
        "checkpointId": cp.checkpoint_id,
        "status": cp.status,
        "currentStep": cp.current_step,
        "completedSteps": cp.completed_steps_json,
        "pendingSteps": cp.pending_steps_json,
        "retryCounters": cp.retry_counters_json,
        "budgetState": cp.budget_state_json,
        "approvalState": cp.approval_state_json,
        "verificationResults": cp.verification_results_json,
        "checkpointVersion": cp.checkpoint_version,
        "isSafeResumable": cp.is_safe_resumable,
        "createdAt": cp.created_at.isoformat() if cp.created_at else "",
    }


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_mission(
    payload: MissionCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    mission = MissionModel(
        title=payload.title,
        goal=payload.goal,
        category=payload.category,
        status=payload.status,
        assigned_agent=payload.assignedAgent,
        metadata_json={},
    )
    db.add(mission)
    await db.commit()
    await db.refresh(mission)

    for task_data in payload.tasks:
        task = MissionTaskModel(
            mission_id=mission.id,
            task_order=task_data.taskOrder,
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            assigned_agent=task_data.assignedAgent,
            dependencies_json=task_data.dependencies,
        )
        db.add(task)

    await db.commit()
    await db.refresh(mission)

    stmt = select(MissionModel).where(MissionModel.id == mission.id)
    res = await db.execute(stmt)
    full_mission = res.scalar_one()
    return format_mission(full_mission)


@router.get("", response_model=List[dict])
async def list_missions(
    category: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(MissionModel)
    if category:
        stmt = stmt.where(MissionModel.category == category)
    if status_filter:
        stmt = stmt.where(MissionModel.status == status_filter)

    result = await db.execute(stmt)
    missions = result.scalars().all()
    return [format_mission(m) for m in missions]


@router.get("/{mission_id}", response_model=dict)
async def get_mission(mission_id: str, db: AsyncSession = Depends(get_db)):
    try:
        u_id = uuid.UUID(mission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mission ID UUID format.")

    stmt = select(MissionModel).where(MissionModel.id == u_id)
    result = await db.execute(stmt)
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found.")

    return format_mission(mission)


@router.post("/{mission_id}/pause", response_model=dict)
async def pause_mission(mission_id: str, db: AsyncSession = Depends(get_db)):
    try:
        u_id = uuid.UUID(mission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mission ID UUID format.")

    stmt = select(MissionModel).where(MissionModel.id == u_id)
    res = await db.execute(stmt)
    mission = res.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    mission.status = "PAUSED"
    await db.commit()
    await db.refresh(mission)
    return format_mission(mission)


@router.post("/{mission_id}/resume", response_model=dict)
async def resume_mission(mission_id: str, db: AsyncSession = Depends(get_db)):
    try:
        u_id = uuid.UUID(mission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mission ID UUID format.")

    stmt = select(MissionModel).where(MissionModel.id == u_id)
    res = await db.execute(stmt)
    mission = res.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    mission.status = "EXECUTING"
    await db.commit()
    await db.refresh(mission)
    return format_mission(mission)


@router.post("/{mission_id}/cancel", response_model=dict)
async def cancel_mission(mission_id: str, db: AsyncSession = Depends(get_db)):
    try:
        u_id = uuid.UUID(mission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mission ID UUID format.")

    stmt = select(MissionModel).where(MissionModel.id == u_id)
    res = await db.execute(stmt)
    mission = res.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    mission.status = "CANCELLED"
    await db.commit()
    await db.refresh(mission)
    return format_mission(mission)


@router.get("/{mission_id}/checkpoints", response_model=List[dict])
async def list_checkpoints(mission_id: str, db: AsyncSession = Depends(get_db)):
    try:
        u_id = uuid.UUID(mission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mission ID UUID format.")

    stmt = select(MissionCheckpointModel).where(MissionCheckpointModel.mission_id == u_id)
    res = await db.execute(stmt)
    checkpoints = res.scalars().all()
    return [format_checkpoint(c) for c in checkpoints]


@router.post("/{mission_id}/checkpoints", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_checkpoint(
    mission_id: str,
    payload: CheckpointCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    try:
        u_id = uuid.UUID(mission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mission ID UUID format.")

    cp = MissionCheckpointModel(
        mission_id=u_id,
        execution_id=payload.executionId,
        checkpoint_id=payload.checkpointId,
        status=payload.status,
        current_step=payload.currentStep,
        completed_steps_json=payload.completedSteps,
        pending_steps_json=payload.pendingSteps,
        retry_counters_json=payload.retryCounters,
        budget_state_json=payload.budgetState,
        approval_state_json=payload.approvalState,
        verification_results_json=payload.verificationResults,
        checkpoint_version=payload.checkpointVersion,
        is_safe_resumable=payload.isSafeResumable,
    )
    db.add(cp)
    await db.commit()
    await db.refresh(cp)
    return format_checkpoint(cp)


@router.get("/{mission_id}/execution-history", response_model=dict)
async def get_execution_history(mission_id: str, db: AsyncSession = Depends(get_db)):
    try:
        u_id = uuid.UUID(mission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mission ID UUID format.")

    cp_stmt = select(MissionCheckpointModel).where(MissionCheckpointModel.mission_id == u_id)
    cp_res = await db.execute(cp_stmt)
    cps = cp_res.scalars().all()

    rec_stmt = select(MissionRecoveryEventModel).where(MissionRecoveryEventModel.mission_id == u_id)
    rec_res = await db.execute(rec_stmt)
    recs = rec_res.scalars().all()

    return {
        "missionId": mission_id,
        "checkpointsCount": len(cps),
        "checkpoints": [format_checkpoint(c) for c in cps],
        "recoveryEvents": [
            {
                "id": str(r.id),
                "stepId": r.step_id,
                "strategyUsed": r.strategy_used,
                "retryCount": r.retry_count,
                "errorType": r.error_type,
                "outcomeStatus": r.outcome_status,
                "details": r.details_json,
                "createdAt": r.created_at.isoformat() if r.created_at else "",
            }
            for r in recs
        ],
    }


@router.get("/{mission_id}/approval", response_model=dict)
async def get_approval_request(mission_id: str, db: AsyncSession = Depends(get_db)):
    try:
        u_id = uuid.UUID(mission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mission ID UUID format.")

    stmt = select(MissionApprovalModel).where(MissionApprovalModel.mission_id == u_id)
    res = await db.execute(stmt)
    approval = res.scalars().first()
    if not approval:
        return {"missionId": mission_id, "hasPendingApproval": False}

    return {
        "id": str(approval.id),
        "missionId": str(approval.mission_id),
        "stepId": approval.step_id,
        "toolName": approval.tool_name,
        "riskLevel": approval.risk_level,
        "targetDetails": approval.target_details_json,
        "reason": approval.reason,
        "status": approval.status,
        "hasPendingApproval": approval.status == "PENDING",
    }


@router.post("/{mission_id}/approval", response_model=dict)
async def respond_approval(
    mission_id: str,
    payload: ApprovalActionSchema,
    db: AsyncSession = Depends(get_db)
):
    try:
        u_id = uuid.UUID(mission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mission ID UUID format.")

    stmt = select(MissionApprovalModel).where(MissionApprovalModel.mission_id == u_id)
    res = await db.execute(stmt)
    approval = res.scalars().first()
    if not approval:
        raise HTTPException(status_code=404, detail="No approval request found for mission")

    approval.status = "APPROVED" if payload.approved else "REJECTED"
    approval.authorized_by = payload.authorizedBy
    await db.commit()

    mission_stmt = select(MissionModel).where(MissionModel.id == u_id)
    m_res = await db.execute(mission_stmt)
    mission = m_res.scalar_one_or_none()
    if mission:
        mission.status = "EXECUTING" if payload.approved else "CANCELLED"
        await db.commit()

    return {"message": f"Approval status updated to {approval.status}", "approved": payload.approved}


@router.delete("/{mission_id}", status_code=status.HTTP_200_OK)
async def delete_mission(mission_id: str, db: AsyncSession = Depends(get_db)):
    try:
        u_id = uuid.UUID(mission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mission ID UUID format.")

    stmt = select(MissionModel).where(MissionModel.id == u_id)
    result = await db.execute(stmt)
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found.")

    await db.delete(mission)
    await db.commit()
    return {"message": f"Mission {mission_id} successfully deleted."}
