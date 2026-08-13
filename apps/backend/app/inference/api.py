"""Inference Gateway REST API Endpoints Module.

Provides OpenAPI-compliant endpoints for chat completion, SSE token streaming,
task classification, model catalog, provider listing, telemetry statistics, and health diagnostics,
guarded by RBAC permissions.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.identity.infrastructure.rbac import PermissionChecker
from app.inference.repository import InferenceRepository
from app.inference.service import (
    InferenceService,
    GatewayService,
    ModelService,
    StreamingService,
    BenchmarkService,
)
from app.inference.schemas import (
    ChatInferenceRequest,
    ChatInferenceResponse,
    TaskClassificationRequest,
    TaskClassificationResponse,
    ModelCatalogItem,
    InferenceHealthResponse,
    InferenceStatisticsResponse,
)

router = APIRouter(prefix="/api/v1/inference", tags=["Enterprise Inference Gateway"])

# Permission dependencies
require_inference_chat = Depends(PermissionChecker("inference:chat"))
require_inference_stream = Depends(PermissionChecker("inference:stream"))
require_inference_admin = Depends(PermissionChecker("inference:admin"))


@router.post("/chat", response_model=ChatInferenceResponse, status_code=status.HTTP_200_OK, dependencies=[require_inference_chat])
async def chat_inference(request: ChatInferenceRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Executes chat completion request through model routing and GPU scheduling."""
    service = InferenceService(repository=InferenceRepository(db))
    return await service.execute_chat(request)


@router.post("/stream", dependencies=[require_inference_stream])
async def stream_inference(request: ChatInferenceRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Streams SSE token completion chunks for prompt query."""
    service = StreamingService(repository=InferenceRepository(db))
    model = request.model or "llama3.2"
    provider = request.provider or "ollama"

    async def event_generator():
        async for chunk in service.stream_chat(request.prompt, model=model, provider=provider):
            yield f"data: {chunk['text']}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/classify", response_model=TaskClassificationResponse, dependencies=[require_inference_chat])
async def classify_task(request: TaskClassificationRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Classifies task intent category and detects required capabilities."""
    service = GatewayService(repository=InferenceRepository(db))
    return service.classify_task(request)


@router.get("/models", response_model=List[ModelCatalogItem], dependencies=[require_inference_chat])
async def list_models(db: AsyncSession = Depends(get_db)) -> Any:
    """Lists registered AI models in catalog."""
    service = ModelService(repository=InferenceRepository(db))
    return service.list_models()


@router.get("/providers", dependencies=[require_inference_chat])
async def list_providers(db: AsyncSession = Depends(get_db)) -> Any:
    """Lists registered local and cloud AI providers."""
    service = ModelService(repository=InferenceRepository(db))
    return service.list_providers()


@router.get("/statistics", response_model=InferenceStatisticsResponse, dependencies=[require_inference_admin])
async def get_inference_statistics(db: AsyncSession = Depends(get_db)) -> Any:
    """Returns inference gateway telemetry statistics."""
    service = BenchmarkService(repository=InferenceRepository(db))
    return await service.get_statistics()


@router.get("/health", response_model=InferenceHealthResponse, dependencies=[require_inference_chat])
async def get_inference_health(db: AsyncSession = Depends(get_db)) -> Any:
    """Runs gateway diagnostic health checks."""
    service = BenchmarkService(repository=InferenceRepository(db))
    return await service.check_health()
