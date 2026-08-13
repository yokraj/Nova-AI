"""Symbol Indexer Module.

Builds searchable symbol tables across modules, packages, classes, functions,
methods, routes, and database tables.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class SymbolIndexer:
    """Enterprise Source Code Symbol Table Indexer."""

    def __init__(self) -> None:
        self._symbol_table: Dict[str, List[Dict[str, Any]]] = {}
        logger.info("symbol_indexer_initialized")

    def index_symbols(self, repository_id: str, file_path: str, symbols: List[Dict[str, Any]]) -> None:
        """Indexes symbols into global repository symbol table."""
        if repository_id not in self._symbol_table:
            self._symbol_table[repository_id] = []

        for sym in symbols:
            sym_entry = dict(sym)
            sym_entry["repository_id"] = repository_id
            sym_entry["file_path"] = file_path
            self._symbol_table[repository_id].append(sym_entry)

        logger.info("symbols_indexed", repository_id=repository_id, count=len(symbols))

    def search_symbols(self, repository_id: str, query: str = "") -> List[Dict[str, Any]]:
        """Searches symbol table by repository ID and name query."""
        symbols = self._symbol_table.get(repository_id, [])
        if not query:
            return symbols
        q_lower = query.lower()
        return [s for s in symbols if q_lower in s["name"].lower()]
