"""Inference Gateway Repository Module.

Provides asynchronous database access for inference requests, registered model catalog,
token logs, and gateway statistics.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
import structlog

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.inference.models import (
    InferenceRequestModel,
    RegisteredModelRecord,
    TokenLogModel,
    InferenceStatisticsModel,
)

logger = structlog.get_logger(__name__)


class InferenceRepository:
    """Enterprise Inference Gateway Database Repository."""

    def __init__(self, session: Optional[AsyncSession] = None) -> None:
        self.session = session
        self._in_memory_requests: Dict[str, InferenceRequestModel] = {}

    async def save_request_log(
        self,
        prompt: str,
        model_name: str,
        provider: str,
        task_category: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
    ) -> InferenceRequestModel:
        """Saves an inference request execution log."""
        req_id = str(uuid.uuid4())
        total_tokens = prompt_tokens + completion_tokens
        record = InferenceRequestModel(
            id=req_id,
            prompt=prompt,
            model_name=model_name,
            provider=provider,
            task_category=task_category,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            status="completed",
            created_at=datetime.now(timezone.utc),
        )

        self._in_memory_requests[req_id] = record

        if self.session is not None:
            try:
                self.session.add(record)
                await self.session.commit()
            except Exception:
                pass

        logger.info("inference_request_logged", id=req_id, model=model_name, total_tokens=total_tokens)
        return record

    async def get_request_log(self, request_id: str) -> Optional[InferenceRequestModel]:
        """Fetches inference request record by ID."""
        if self.session is not None:
            try:
                stmt = select(InferenceRequestModel).where(InferenceRequestModel.id == request_id)
                res = await self.session.execute(stmt)
                item = res.scalar_one_or_none()
                if item:
                    return item
            except Exception:
                pass
        return self._in_memory_requests.get(request_id)

    async def count_requests(self) -> int:
        """Returns total requests count."""
        if self.session is not None:
            try:
                count = await self.session.scalar(select(func.count(InferenceRequestModel.id)))
                if count is not None:
                    return count
            except Exception:
                pass
        return len(self._in_memory_requests)
