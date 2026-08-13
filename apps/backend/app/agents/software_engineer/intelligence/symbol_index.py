"""Symbol Index managing in-memory symbol tables and reference lookups.
"""

from typing import Dict, List, Optional

from app.agents.software_engineer.intelligence.interfaces import SymbolIndexer
from app.agents.software_engineer.intelligence.models import Symbol


class InMemorySymbolIndex(SymbolIndexer):
    """Provides fast lookup of indexed symbols and track their references."""

    def __init__(self) -> None:
        # Maps qualified name to Symbol object
        self._index: Dict[str, Symbol] = {}
        # Maps file path to list of symbol qualified names declared in it
        self._file_symbols: Dict[str, List[str]] = {}

    def index_symbols(self, file_path: str, symbols: List[Symbol]) -> None:
        """Indexes symbols declared inside a single file.

        Args:
            file_path: Relative file path.
            symbols: List of discovered symbols.
        """
        # Remove previously indexed symbols for this file to support clean incremental replacement
        if file_path in self._file_symbols:
            for old_fqn in self._file_symbols[file_path]:
                self._index.pop(old_fqn, None)

        self._file_symbols[file_path] = []
        for sym in symbols:
            self._index[sym.fully_qualified_name] = sym
            self._file_symbols[file_path].append(sym.fully_qualified_name)

    def lookup_symbol(self, qualified_name: str) -> Optional[Symbol]:
        """Looks up a symbol by its fully qualified name.

        Args:
            qualified_name: Qualified name (e.g. app.main.start).

        Returns:
            Symbol instance or None.
        """
        # First check exact match
        if qualified_name in self._index:
            return self._index[qualified_name]

        # Check partial or suffix matches (e.g. ClassName.method)
        for fqn, sym in self._index.items():
            if fqn.endswith("." + qualified_name) or qualified_name == sym.name:
                return sym

        return None

    def list_symbols(self) -> List[Symbol]:
        """Lists all symbols in the index.

        Returns:
            List of Symbol objects.
        """
        return list(self._index.values())

    def clear(self) -> None:
        """Clears the search indexes."""
        self._index.clear()
        self._file_symbols.clear()
