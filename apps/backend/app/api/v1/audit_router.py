"""FastAPI REST router for Audit Events.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database.session import get_db
from app.database.models.audit_model import AuditEventModel

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditEventCreateSchema(BaseModel):
    eventType: str
    action: str
    toolName: Optional[str] = None
    riskLevel: str = "SAFE"
    actor: str = "User"
    decision: str = "ALLOWED"
    details: dict = Field(default_factory=dict)


def format_audit_event(event: AuditEventModel) -> dict:
    return {
        "id": str(event.id),
        "eventType": event.event_type,
        "action": event.action,
        "toolName": event.tool_name,
        "riskLevel": event.risk_level,
        "actor": event.actor,
        "decision": event.decision,
        "details": event.details_json or {},
        "createdAt": event.created_at.isoformat() if event.created_at else "",
    }


@router.post("/events", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_audit_event(
    payload: AuditEventCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    event = AuditEventModel(
        event_type=payload.eventType,
        action=payload.action,
        tool_name=payload.toolName,
        risk_level=payload.riskLevel,
        actor=payload.actor,
        decision=payload.decision,
        details_json=payload.details,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return format_audit_event(event)


@router.get("/events", response_model=List[dict])
async def list_audit_events(
    event_type: Optional[str] = Query(None, alias="type"),
    risk_level: Optional[str] = Query(None, alias="risk"),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AuditEventModel).order_by(desc(AuditEventModel.created_at)).limit(limit)
    if event_type:
        stmt = stmt.where(AuditEventModel.event_type == event_type)
    if risk_level:
        stmt = stmt.where(AuditEventModel.risk_level == risk_level)

    result = await db.execute(stmt)
    events = result.scalars().all()
    return [format_audit_event(e) for e in events]
