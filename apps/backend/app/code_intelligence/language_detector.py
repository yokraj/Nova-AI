"""Language Detector Module.

Detects 19 programming and markup languages based on file extensions, filenames,
and shebang header fingerprints.
"""

import os
from typing import Any, Dict, Optional
import structlog

from app.code_intelligence.config import CodeIntelligenceConfig

logger = structlog.get_logger(__name__)


class LanguageDetector:
    """Enterprise Source Code Language Detector."""

    def __init__(self, config: Optional[CodeIntelligenceConfig] = None) -> None:
        self.config = config or CodeIntelligenceConfig()
        logger.info("language_detector_initialized")

    def detect_language(self, file_path: str, content: Optional[str] = None) -> str:
        """Detects language for file path or content header."""
        basename = os.path.basename(file_path).lower()
        if basename == "dockerfile":
            return "Dockerfile"

        _, ext = os.path.splitext(file_path)
        ext_lower = ext.lower()

        if ext_lower in self.config.language_extension_map:
            return self.config.language_extension_map[ext_lower]

        # Content Shebang Fallback
        if content and content.startswith("#!"):
            first_line = content.split("\n")[0].lower()
            if "python" in first_line:
                return "Python"
            elif "node" in first_line:
                return "JavaScript"
            elif "bash" in first_line or "sh" in first_line:
                return "Shell"

        return "Unknown"
