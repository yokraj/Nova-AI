"""Code Intelligence Configuration Module.

Defines Pydantic settings for repository file bounds, batch chunk sizes,
supported file extension mappings, and AST parser bounds.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CodeIntelligenceConfig(BaseModel):
    """Configuration settings for Enterprise Document & Code Intelligence Engine."""

    # File & Repository Bounds
    max_file_size_bytes: int = Field(default=10 * 1024 * 1024, description="Maximum single file size limit (10MB)")
    batch_indexing_chunk_size: int = Field(default=100, description="Max file batch count per indexing cycle")
    max_ast_recursion_depth: int = Field(default=50, description="Max depth for AST node traversal")

    # Extension Mappings for 19 Supported Languages
    language_extension_map: Dict[str, str] = Field(
        default_factory=lambda: {
            ".py": "Python",
            ".java": "Java",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".jsx": "JavaScript",
            ".go": "Go",
            ".rs": "Rust",
            ".cs": "C#",
            ".cpp": "C++",
            ".h": "C++",
            ".kt": "Kotlin",
            ".swift": "Swift",
            ".sql": "SQL",
            ".html": "HTML",
            ".css": "CSS",
            ".json": "JSON",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".md": "Markdown",
            ".xml": "XML",
            ".sh": "Shell",
            ".bash": "Shell",
            "dockerfile": "Dockerfile",
        }
    )

    # Document Extension Mappings for 14 Supported Document Formats
    document_extension_map: Dict[str, str] = Field(
        default_factory=lambda: {
            ".pdf": "PDF",
            ".docx": "DOCX",
            ".txt": "TXT",
            ".md": "Markdown",
            ".html": "HTML",
            ".csv": "CSV",
            ".json": "JSON",
            ".xml": "XML",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".puml": "PlantUML",
            ".mmd": "Mermaid",
        }
    )
