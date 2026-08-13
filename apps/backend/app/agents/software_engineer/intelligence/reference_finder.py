"""Locates definition locations and occurrences of symbols across codebase files.
"""

import ast
from typing import Any, Dict, List

from app.agents.software_engineer.intelligence.models import Symbol


class ReferenceFinder:
    """Finds cross-references of symbols across parsed AST trees."""

    def resolve_references(self, ast_trees: Dict[str, Any], symbols: Dict[str, Symbol]) -> None:
        """Finds all usages of indexed symbols across the parsed ASTs, updating Symbol.references.

        Args:
            ast_trees: Mapping of relative path to parsed raw AST.
            symbols: Mapping of qualified name to Symbol.
        """
        # Mapping from symbol name to its qualified name(s)
        name_to_fqns: Dict[str, List[str]] = {}
        for fqn, sym in symbols.items():
            name_to_fqns.setdefault(sym.name, []).append(fqn)

        # Scan all files
        for file_path, raw_ast in ast_trees.items():
            if not raw_ast:
                continue

            for node in ast.walk(raw_ast):
                ref_name = None

                # Match names, e.g. start() or start
                if isinstance(node, ast.Name):
                    ref_name = node.id
                # Match attributes, e.g. self.attr or obj.attr
                elif isinstance(node, ast.Attribute):
                    ref_name = node.attr

                if ref_name and ref_name in name_to_fqns:
                    for fqn in name_to_fqns[ref_name]:
                        # Do not count self-reference (definition line) as a reference
                        sym = symbols[fqn]
                        if sym.file_path == file_path and getattr(node, "lineno", -1) == sym.line_number:
                            continue

                        # Add reference path if not already present
                        if file_path not in sym.references:
                            sym.references.append(file_path)
