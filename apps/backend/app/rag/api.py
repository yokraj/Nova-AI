"""RAG REST API Endpoints Module.

Provides OpenAPI-compliant endpoints for grounded RAG queries, candidate retrieval,
LLM context package assembly, telemetry statistics, and health diagnostics, guarded by RBAC permissions.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.identity.infrastructure.rbac import PermissionChecker
from app.rag.engine import HybridRAGEngine
from app.rag.retriever import HybridRAGRetriever
from app.rag.context_builder import ContextBuilder

router = APIRouter(prefix="/api/v1/rag", tags=["Enterprise Hybrid RAG"])

# Permission dependencies
require_rag_query = Depends(PermissionChecker("rag:query"))
require_rag_read = Depends(PermissionChecker("rag:read"))
require_rag_admin = Depends(PermissionChecker("rag:admin"))


class RAGQueryRequest(BaseModel):
    """Request schema for grounded RAG query execution."""

    query: str = Field(min_length=1, description="User query text")
    workspace: str = Field(default="Nova", description="Target workspace partition")
    project: Optional[str] = Field(default=None, description="Optional active project filter")
    conversation_id: str = Field(default="default", description="Conversation thread ID")
    conversation_history: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    user_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)


class RAGRetrieveRequest(BaseModel):
    """Request schema for candidate retrieval."""

    query: str = Field(min_length=1)
    workspace: Optional[str] = Field(default="Nova")
    project: Optional[str] = Field(default=None)


class RAGContextRequest(BaseModel):
    """Request schema for context package assembly."""

    query: str = Field(min_length=1)
    workspace: str = Field(default="Nova")
    project: Optional[str] = Field(default=None)


@router.post("/query", status_code=status.HTTP_200_OK, dependencies=[require_rag_query])
async def execute_rag_query(request: RAGQueryRequest) -> Any:
    """Executes full grounded Hybrid RAG query pipeline."""
    engine = HybridRAGEngine()
    return await engine.execute_grounded_query(
        query=request.query,
        workspace=request.workspace,
        project=request.project,
        conversation_id=request.conversation_id,
        conversation_history=request.conversation_history,
        user_preferences=request.user_preferences,
    )


@router.post("/retrieve", status_code=status.HTTP_200_OK, dependencies=[require_rag_read])
async def retrieve_candidates(request: RAGRetrieveRequest) -> Any:
    """Retrieves top reranked hybrid search candidates."""
    retriever = HybridRAGRetriever()
    return await retriever.retrieve_grounded_context(
        query=request.query, workspace=request.workspace, project=request.project
    )


@router.post("/context", status_code=status.HTTP_200_OK, dependencies=[require_rag_read])
async def assemble_context(request: RAGContextRequest) -> Any:
    """Assembles structured LLM context package."""
    retriever = HybridRAGRetriever()
    retrieval_res = await retriever.retrieve_grounded_context(query=request.query, workspace=request.workspace, project=request.project)
    builder = ContextBuilder()
    return builder.build_context_package(
        retrieved_chunks=retrieval_res["selected_chunks"], workspace=request.workspace, project=request.project
    )


@router.get("/statistics", dependencies=[require_rag_read])
async def get_rag_statistics() -> Any:
    """Returns RAG platform statistics telemetry."""
    engine = HybridRAGEngine()
    return engine.stats_tracker.get_statistics()


@router.get("/health", dependencies=[require_rag_read])
async def get_rag_health() -> Any:
    """Runs RAG pipeline diagnostic health checks."""
    engine = HybridRAGEngine()
    return engine.health_checker.run_health_checks()
