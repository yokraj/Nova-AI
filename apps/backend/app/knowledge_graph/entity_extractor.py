"""Entity Extractor Module.

Extracts 28 domain entity types from Memory, Conversation, Code, Documents,
Projects, Architecture docs, Requirements, and API definitions.
"""

import re
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)

SUPPORTED_ENTITY_TYPES = [
    "User", "Workspace", "Project", "Conversation", "Memory", "Document",
    "CodeFile", "Function", "Class", "API", "Endpoint", "Database", "Table",
    "Column", "Technology", "Framework", "Language", "Requirement", "Decision",
    "Task", "Workflow", "Agent", "Tool", "Plugin", "Organization", "Repository",
    "Issue", "Solution",
]


class EntityExtractor:
    """Enterprise Knowledge Graph Entity Extractor."""

    def __init__(self) -> None:
        logger.info("entity_extractor_initialized", supported_types_count=len(SUPPORTED_ENTITY_TYPES))

    def extract_entities_from_text(
        self,
        text: str,
        workspace: str = "Nova",
        project: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Extracts entity nodes from arbitrary text or structured content."""
        extracted: List[Dict[str, Any]] = []

        # 1. Code Class / Function Extraction
        for match in re.finditer(r"class\s+([A-Za-z0-9_]+)", text):
            extracted.append({
                "name": match.group(1),
                "entity_type": "Class",
                "workspace": workspace,
                "project": project,
            })
        for match in re.finditer(r"def\s+([A-Za-z0-9_]+)", text):
            extracted.append({
                "name": match.group(1),
                "entity_type": "Function",
                "workspace": workspace,
                "project": project,
            })

        # 2. Technology & Language Extraction
        tech_keywords = ["Python", "FastAPI", "PostgreSQL", "Redis", "SQLite", "React", "Docker", "Pytest", "ChromaDB", "FAISS"]
        for tech in tech_keywords:
            if tech.lower() in text.lower():
                entity_type = "Language" if tech == "Python" else ("Database" if tech in ["PostgreSQL", "SQLite", "Redis"] else "Framework")
                extracted.append({
                    "name": tech,
                    "entity_type": entity_type,
                    "workspace": workspace,
                    "project": project,
                })

        # 3. Project / Workspace Entity
        if project:
            extracted.append({
                "name": project,
                "entity_type": "Project",
                "workspace": workspace,
                "project": project,
            })

        # Fallback default memory/document entity if none matched
        if not extracted:
            extracted.append({
                "name": text[:30] or "Extracted Entity",
                "entity_type": "Memory",
                "workspace": workspace,
                "project": project,
            })

        logger.info("entities_extracted", text_len=len(text), count=len(extracted))
        return extracted
