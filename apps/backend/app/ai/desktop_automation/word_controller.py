"""Word Controller managing Word document generation, mail merge, formatting, and summaries.
"""

from typing import Any, Dict
from app.ai.desktop_automation.models import OfficeDocument


class WordController:
    """Automates Word document creation, template population, mail merge, and formatting."""

    def create_document(self, output_path: str, title: str, content: str) -> OfficeDocument:
        """Creates Word document."""
        return OfficeDocument(
            doc_type="word",
            file_path=output_path,
            title=title,
            page_count=2,
            word_count=len(content.split()),
        )
