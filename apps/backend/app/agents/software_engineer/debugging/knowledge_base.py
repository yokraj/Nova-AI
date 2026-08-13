"""Knowledge Base tracking histories of previous debug session reports.
"""

import json
import os
from typing import List

from app.agents.software_engineer.debugging.interfaces import KnowledgeBase
from app.agents.software_engineer.debugging.models import DebugReport


class LocalKnowledgeBase(KnowledgeBase):
    """Indices report details locally."""

    def __init__(self, kb_file_path: str) -> None:
        self.kb_file_path = os.path.abspath(kb_file_path)
        self.entries: List[dict] = []
        self.load()

    def load(self) -> None:
        if os.path.exists(self.kb_file_path):
            try:
                with open(self.kb_file_path, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
            except Exception:
                self.entries = []

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.kb_file_path), exist_ok=True)
        try:
            with open(self.kb_file_path, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2)
        except Exception:
            pass

    def search_knowledge(self, query: str) -> List[DebugReport]:
        """Queries historical entries matched by keywords.

        Args:
            query: Keyword query string.

        Returns:
            List of DebugReport.
        """
        results: List[DebugReport] = []
        query_lower = query.lower()

        for item in self.entries:
            try:
                report = DebugReport.model_validate(item)
                txt = report.markdown_report.lower()
                if query_lower in txt or query_lower in report.failure.traceback.exception_message.lower():
                    results.append(report)
            except Exception:
                continue

        return results

    def index_report(self, report: DebugReport) -> None:
        self.entries.append(report.model_dump())
        self.save()
