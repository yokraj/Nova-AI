"""Repository Summary Module.

Compiles executive architectural summaries of entire repositories.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.code_intelligence.schemas import RepositorySummaryResponse

logger = structlog.get_logger(__name__)


class RepositorySummaryEngine:
    """Enterprise Executive Repository Summary Generator."""

    def __init__(self) -> None:
        logger.info("repository_summary_engine_initialized")

    def generate_repository_summary(
        self,
        repository_id: str,
        name: str,
        primary_language: str,
        frameworks: List[str],
        file_count: int,
        lines_of_code: int,
        symbols_count: int,
        apis_count: int,
        tables_count: int,
    ) -> RepositorySummaryResponse:
        """Generates structured architectural summary DTO for target repository."""
        summary_text = (
            f"Repository '{name}' is built primarily in {primary_language} with frameworks: {', '.join(frameworks) or 'Standard Library'}. "
            f"It comprises {file_count} files, approx {lines_of_code} LOC, {symbols_count} code symbols, "
            f"{apis_count} API endpoints, and {tables_count} database tables."
        )

        logger.info("repository_summary_generated", repository_id=repository_id, name=name)
        return RepositorySummaryResponse(
            repository_id=repository_id,
            name=name,
            primary_language=primary_language,
            frameworks=frameworks,
            file_count=file_count,
            lines_of_code=lines_of_code,
            architecture_summary=summary_text,
            key_symbols_count=symbols_count,
            api_endpoints_count=apis_count,
            database_tables_count=tables_count,
        )
