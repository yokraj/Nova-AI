"""Code Intelligence Schemas Module.

Defines Pydantic DTO request/response schemas for repository indexing, code symbols,
dependencies, architecture patterns, APIs, databases, health reports, and telemetry statistics.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class RepositoryIndexRequest(BaseModel):
    """Request schema for indexing a source code repository."""

    name: str = Field(min_length=1, description="Repository project name")
    root_path: str = Field(min_length=1, description="Root directory path on filesystem")
    workspace: str = Field(default="Nova", description="Target workspace partition")


class RepositoryResponse(BaseModel):
    """Response DTO for indexed repository."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    root_path: str
    primary_language: str
    frameworks: List[str] = Field(default_factory=list)
    file_count: int
    lines_of_code: int
    workspace: str
    created_at: datetime


class CodeSymbolResponse(BaseModel):
    """Response DTO for indexed code symbol."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    repository_id: str
    name: str
    symbol_type: str
    file_path: str
    start_line: int
    end_line: int
    signature: Optional[str] = None
    docstring: Optional[str] = None


class ArchitecturePatternResponse(BaseModel):
    """Response DTO for detected software architecture pattern."""

    pattern_name: str
    component_name: str
    file_paths: List[str]
    description: Optional[str] = None


class APISchemaResponse(BaseModel):
    """Response DTO for extracted API endpoints."""

    endpoint: str
    http_method: str
    file_path: str
    function_name: str
    summary: Optional[str] = None


class DatabaseSchemaResponse(BaseModel):
    """Response DTO for extracted ORM model or SQL database table."""

    table_name: str
    columns: List[Dict[str, Any]]
    file_path: str


class RepositorySummaryResponse(BaseModel):
    """Response DTO for repository executive architectural summary."""

    repository_id: str
    name: str
    primary_language: str
    frameworks: List[str]
    file_count: int
    lines_of_code: int
    architecture_summary: str
    key_symbols_count: int
    api_endpoints_count: int
    database_tables_count: int


class CodeHealthResponse(BaseModel):
    """Health diagnostic report for code intelligence engine."""

    status: str = "healthy"
    parser_healthy: bool = True
    indexer_healthy: bool = True
    dependency_graph_healthy: bool = True
    symbol_graph_healthy: bool = True
    details: Dict[str, Any] = Field(default_factory=dict)


class CodeStatisticsResponse(BaseModel):
    """Telemetry metrics summary for code intelligence engine."""

    model_config = ConfigDict(from_attributes=True)

    repositories_indexed: int
    files_indexed: int
    classes_indexed: int
    functions_indexed: int
    apis_indexed: int
    tables_indexed: int
    relationships_discovered: int
    indexing_latency: float
    storage_usage: int
    timestamp: datetime
