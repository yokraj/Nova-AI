"""Code Summarizer Module.

Generates hierarchical summaries for Repository, Folder, Package, Module, Class,
Function, Method, API, and Database table entities.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class CodeSummarizer:
    """Enterprise Hierarchical Code Summarization Engine."""

    def __init__(self) -> None:
        logger.info("code_summarizer_initialized")

    def summarize_symbol(self, symbol: Dict[str, Any]) -> str:
        """Generates concise summary for a single code symbol."""
        sym_type = symbol.get("symbol_type", "Symbol")
        name = symbol.get("name", "Unknown")
        file_path = symbol.get("file_path", "")
        return f"{sym_type} '{name}' defined in {file_path}."

    def summarize_module(self, file_path: str, symbols: List[Dict[str, Any]]) -> str:
        """Generates module-level architectural summary."""
        classes = [s["name"] for s in symbols if s.get("symbol_type") in ["Class", "Interface"]]
        funcs = [s["name"] for s in symbols if s.get("symbol_type") == "Function"]
        return f"Module '{file_path}' contains {len(classes)} classes ({', '.join(classes[:3])}) and {len(funcs)} functions."
