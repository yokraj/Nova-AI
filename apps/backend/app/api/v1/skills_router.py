"""FastAPI REST router for Skills and Version management.
"""

from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.database.session import get_db
from app.database.models.skill_model import SkillModel, SkillVersionModel

router = APIRouter(prefix="/skills", tags=["skills"])


# Pydantic Schemas
class SkillTriggerSchema(BaseModel):
    naturalLanguagePattern: str
    intent: str = "workflow_execution"
    confidence: float = 0.95


class SkillVariableSchema(BaseModel):
    name: str
    type: str = "string"
    description: str = ""
    required: bool = True
    defaultValue: Optional[str] = None
    examples: List[str] = Field(default_factory=list)


class SkillStepSchema(BaseModel):
    id: str
    order: int
    tool: str
    arguments: dict = Field(default_factory=dict)
    argumentTemplates: Optional[dict] = None
    purpose: str = ""
    verification: Optional[dict] = None
    approvalRequired: bool = False


class SkillCreateSchema(BaseModel):
    name: str
    description: str
    purpose: str
    category: str = "general"
    status: str = "active"
    confidence: float = 0.9
    source: str = "user_taught"
    owner: str = "NovaUser"
    triggerPatterns: List[SkillTriggerSchema] = Field(default_factory=list)
    requiredTools: List[str] = Field(default_factory=list)
    variables: List[SkillVariableSchema] = Field(default_factory=list)
    steps: List[SkillStepSchema] = Field(default_factory=list)
    verificationRules: List[str] = Field(default_factory=list)
    recoveryRules: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class SkillUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    purpose: Optional[str] = None
    status: Optional[str] = None
    confidence: Optional[float] = None
    successRate: Optional[float] = None


class SkillResponseSchema(BaseModel):
    id: str
    name: str
    description: str
    purpose: str
    category: str
    version: int
    status: str
    confidence: float
    successRate: float
    usageCount: int
    createdAt: str
    updatedAt: str
    triggerPatterns: list
    requiredTools: list
    variables: list
    steps: list

    model_config = {"from_attributes": True}


def format_skill(skill: SkillModel) -> dict:
    return {
        "id": str(skill.id),
        "name": skill.name,
        "description": skill.description,
        "purpose": skill.purpose,
        "category": skill.category,
        "version": skill.version,
        "status": skill.status,
        "confidence": skill.confidence,
        "successRate": skill.success_rate,
        "usageCount": skill.usage_count,
        "createdAt": skill.created_at.isoformat() if skill.created_at else "",
        "updatedAt": skill.updated_at.isoformat() if skill.updated_at else "",
        "triggerPatterns": skill.trigger_patterns_json or [],
        "requiredTools": skill.required_tools_json or [],
        "variables": skill.variables_json or [],
        "steps": skill.steps_json or [],
    }


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_skill(
    payload: SkillCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    skill = SkillModel(
        name=payload.name,
        description=payload.description,
        purpose=payload.purpose,
        category=payload.category,
        status=payload.status,
        confidence=payload.confidence,
        source=payload.source,
        owner=payload.owner,
        trigger_patterns_json=[tp.model_dump() for tp in payload.triggerPatterns],
        required_tools_json=payload.requiredTools,
        variables_json=[v.model_dump() for v in payload.variables],
        steps_json=[s.model_dump() for s in payload.steps],
        metadata_json={
            "verificationRules": payload.verificationRules,
            "recoveryRules": payload.recoveryRules,
            "constraints": payload.constraints,
            "examples": payload.examples,
            "tags": payload.tags,
        },
    )
    db.add(skill)
    await db.commit()
    await db.refresh(skill)

    initial_version = SkillVersionModel(
        skill_id=skill.id,
        version_number=1,
        changes="Initial skill creation",
        reason="Initial creation from skill router",
        steps_snapshot_json=skill.steps_json,
        success_rate_snapshot=1.0,
    )
    db.add(initial_version)
    await db.commit()

    return format_skill(skill)


@router.get("", response_model=List[dict])
async def list_skills(
    query: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(SkillModel)
    if category:
        stmt = stmt.where(SkillModel.category == category)
    if status_filter:
        stmt = stmt.where(SkillModel.status == status_filter)
    if query:
        q_term = f"%{query}%"
        stmt = stmt.where(or_(SkillModel.name.ilike(q_term), SkillModel.description.ilike(q_term), SkillModel.purpose.ilike(q_term)))

    result = await db.execute(stmt)
    skills = result.scalars().all()
    return [format_skill(s) for s in skills]


@router.get("/{skill_id}", response_model=dict)
async def get_skill(skill_id: str, db: AsyncSession = Depends(get_db)):
    try:
        u_id = uuid.UUID(skill_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid skill ID UUID format.")

    stmt = select(SkillModel).where(SkillModel.id == u_id)
    result = await db.execute(stmt)
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill {skill_id} not found.")

    return format_skill(skill)


@router.put("/{skill_id}", response_model=dict)
async def update_skill(
    skill_id: str,
    payload: SkillUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    try:
        u_id = uuid.UUID(skill_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid skill ID UUID format.")

    stmt = select(SkillModel).where(SkillModel.id == u_id)
    result = await db.execute(stmt)
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill {skill_id} not found.")

    if payload.name is not None:
        skill.name = payload.name
    if payload.description is not None:
        skill.description = payload.description
    if payload.purpose is not None:
        skill.purpose = payload.purpose
    if payload.status is not None:
        skill.status = payload.status
    if payload.confidence is not None:
        skill.confidence = payload.confidence
    if payload.successRate is not None:
        skill.success_rate = payload.successRate

    await db.commit()
    await db.refresh(skill)
    return format_skill(skill)


@router.delete("/{skill_id}", status_code=status.HTTP_200_OK)
async def delete_skill(skill_id: str, db: AsyncSession = Depends(get_db)):
    try:
        u_id = uuid.UUID(skill_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid skill ID UUID format.")

    stmt = select(SkillModel).where(SkillModel.id == u_id)
    result = await db.execute(stmt)
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill {skill_id} not found.")

    await db.delete(skill)
    await db.commit()
    return {"message": f"Skill {skill_id} successfully deleted."}
