"""AST Parser Module.

Implements native Python AST parsing and universal multi-language pattern parsing
for Classes, Interfaces, Functions, Methods, Decorators, Imports, Exports, and Variables.
"""

import ast
import re
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class ASTParser:
    """Enterprise Multi-Language AST & Code Pattern Parser."""

    def __init__(self) -> None:
        logger.info("ast_parser_initialized")

    def parse_source_code(self, source_code: str, language: str = "Python", file_path: str = "") -> Dict[str, Any]:
        """Parses source code into structured AST symbol nodes."""
        symbols: List[Dict[str, Any]] = []
        imports: List[str] = []

        if language == "Python":
            try:
                tree = ast.parse(source_code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        symbols.append({
                            "name": node.name,
                            "symbol_type": "Class",
                            "start_line": getattr(node, "lineno", 1),
                            "end_line": getattr(node, "end_lineno", getattr(node, "lineno", 1)),
                            "docstring": ast.get_docstring(node),
                        })
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        symbols.append({
                            "name": node.name,
                            "symbol_type": "Function",
                            "start_line": getattr(node, "lineno", 1),
                            "end_line": getattr(node, "end_lineno", getattr(node, "lineno", 1)),
                            "docstring": ast.get_docstring(node),
                        })
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
            except SyntaxError:
                # Fallback to regex pattern matching on syntax error
                pass

        # Universal Multi-Language Fallback Parser (JS, TS, Java, Go, Rust, C#, C++)
        if not symbols:
            lines = source_code.splitlines()
            for idx, line in enumerate(lines, 1):
                class_match = re.search(r"\b(class|interface|struct)\s+([A-Za-z0-9_]+)", line)
                if class_match:
                    symbols.append({
                        "name": class_match.group(2),
                        "symbol_type": "Class" if class_match.group(1) == "class" else "Interface",
                        "start_line": idx,
                        "end_line": idx + 5,
                    })

                func_match = re.search(r"\b(def|function|fn|func)\s+([A-Za-z0-9_]+)", line)
                if func_match:
                    symbols.append({
                        "name": func_match.group(2),
                        "symbol_type": "Function",
                        "start_line": idx,
                        "end_line": idx + 5,
                    })

                imp_match = re.search(r"\b(import|require|use|include)\s+['\"]?([A-Za-z0-9_\/\.\-]+)['\"]?", line)
                if imp_match:
                    imports.append(imp_match.group(2))

        logger.info("ast_parsing_completed", language=language, symbol_count=len(symbols), import_count=len(imports))
        return {
            "file_path": file_path,
            "language": language,
            "symbols": symbols,
            "imports": list(set(imports)),
        }
