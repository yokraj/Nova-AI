"""Implements offline keyword and attribute matching semantic searches.
"""

from typing import List

from app.agents.software_engineer.intelligence.interfaces import SemanticSearcher
from app.agents.software_engineer.intelligence.models import SemanticSearchResult, Symbol


class SymbolSemanticSearcher(SemanticSearcher):
    """Weighted search engine indexing and scoring symbols in workspace."""

    def __init__(self, symbols: List[Symbol]) -> None:
        self.symbols = symbols

    def search(self, query: str, limit: int = 10) -> List[SemanticSearchResult]:
        """Queries active symbols database using weighted match heuristics.

        Args:
            query: Target search query string.
            limit: Maximum count of results to return.

        Returns:
            List of sorted SemanticSearchResult models.
        """
        if not query:
            return []

        query_lower = query.lower()
        results: List[SemanticSearchResult] = []

        for sym in self.symbols:
            score = 0.0
            matched_by = ""

            name_lower = sym.name.lower()
            fqn_lower = sym.fully_qualified_name.lower()
            doc_lower = (sym.docstring or "").lower()
            file_lower = sym.file_path.lower()
            sig_lower = (sym.signature or "").lower()

            # Exact Name Match (Highest priority)
            if query_lower == name_lower:
                score += 10.0
                matched_by = "exact_name"
            # Substring Name Match
            elif query_lower in name_lower:
                score += 5.0
                matched_by = "name_substring"
            # Fully Qualified Name Match
            elif query_lower in fqn_lower:
                score += 4.0
                matched_by = "qualified_name"
            # Docstring match
            elif query_lower in doc_lower:
                score += 3.0
                matched_by = "docstring"
            # Signature Match
            elif query_lower in sig_lower:
                score += 2.0
                matched_by = "signature"
            # File path match
            elif query_lower in file_lower:
                score += 1.5
                matched_by = "file_path"

            if score > 0.0:
                results.append(SemanticSearchResult(symbol=sym, score=score, matched_by=matched_by))

        # Sort results by score desc
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]
