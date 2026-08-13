"""Code Parser Coordinator Module.

Coordinates language detection, AST source code parsing, and symbol table extraction.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.code_intelligence.language_detector import LanguageDetector
from app.code_intelligence.ast_parser import ASTParser

logger = structlog.get_logger(__name__)


class CodeParser:
    """Enterprise Master Code Parser Coordinator."""

    def __init__(
        self,
        language_detector: Optional[LanguageDetector] = None,
        ast_parser: Optional[ASTParser] = None,
    ) -> None:
        self.language_detector = language_detector or LanguageDetector()
        self.ast_parser = ast_parser or ASTParser()
        logger.info("code_parser_coordinator_initialized")

    def parse_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Detects language and executes AST symbol parsing."""
        lang = self.language_detector.detect_language(file_path, content=content)
        ast_result = self.ast_parser.parse_source_code(content, language=lang, file_path=file_path)

        logger.info("file_parsed", file_path=file_path, language=lang, symbols_found=len(ast_result["symbols"]))
        return ast_result
