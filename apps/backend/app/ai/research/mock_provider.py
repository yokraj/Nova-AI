"""Mock Research Provider returning deterministic test responses for offline tests and CI.
"""

from typing import Any, Dict, List
from app.ai.research.models import (
    CitationItem,
    KnowledgeSource,
    ReasoningOutput,
    ReportType,
    ResearchReport,
    SourceType,
)


class MockResearchProvider:
    """Mock Research Provider returning deterministic test responses."""

    async def mock_search(self, query: str) -> List[KnowledgeSource]:
        return [
            KnowledgeSource(
                title=f"Mock Source for {query}",
                url_or_path=f"https://mock.nova.ai/{query}",
                type=SourceType.WEB_PAGE,
                trust_score=0.95,
                extracted_text=f"Mock extracted information for {query}",
            )
        ]

    async def mock_generate_report(self, topic: str) -> ResearchReport:
        cite = CitationItem(
            source_title=f"Mock Source for {topic}",
            url_or_path=f"https://mock.nova.ai/{topic}",
            author="Mock Researcher",
            year=2026,
            citation_string=f"Mock Researcher (2026). Mock Source for {topic}.",
        )

        return ResearchReport(
            topic=topic,
            report_type=ReportType.TECHNICAL_REPORT,
            executive_summary=f"[Mock Summary] Autonomous research results for {topic}.",
            technical_details=f"[Mock Technical Details] Architecture, performance, and best practices for {topic}.",
            voice_summary=f"Mock research on {topic} is complete with 95% confidence.",
            citations=[cite],
        )
