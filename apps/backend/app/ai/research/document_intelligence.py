"""Document Intelligence Engine for Nova AI (Vertical 1).

Performs real, verified file extraction, AST code parsing, tabular data parsing,
and multi-format document understanding across TXT, MD, PY, JSON, CSV, PDF, and DOCX.

Guarantees:
- 100% Real Disk Extraction: Never returns fabricated file content or fake tables.
- Workspace Boundary Sandboxing: Restricts reads strictly to authorized workspace roots.
- Path Traversal & Injection Defense: Blocks traversal escapes ('..', symlinks, unauthorized paths).
- Deep Code Intelligence: Extracts classes, methods, functions, docstrings, and imports via Python AST.
- Tabular Intelligence: Parses CSV and document tables into structured 2D matrices.
"""

import ast
import csv
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import structlog

from app.ai.research.interfaces import IDocumentIntelligence
from app.ai.research.models import DocumentAnalysis
from app.security.workspace_guard import (
    WorkspaceSecurityGuard,
    WorkspaceSecurityException,
    ALLOWED_DOCUMENT_EXTENSIONS,
)

logger = structlog.get_logger("document_intelligence")


class DocumentIntelligence(IDocumentIntelligence):
    """Production-grade Document Intelligence Engine parsing real disk files into structured models."""

    def __init__(self, workspace_guard: Optional[WorkspaceSecurityGuard] = None) -> None:
        self.guard = workspace_guard or WorkspaceSecurityGuard()

    async def analyze_document(self, doc_path: str) -> DocumentAnalysis:
        """Parses a target workspace document into verified structured content, tables, and AST symbols.

        Args:
            doc_path: Relative or absolute path to target file within authorized workspace.

        Returns:
            DocumentAnalysis model containing genuine extracted paragraphs, tables, line count, and symbols.

        Raises:
            WorkspaceSecurityException: If target path escapes authorized workspace.
            FileNotFoundError: If the target file does not exist.
            ValueError: If target exceeds size limit or format is unsupported.
        """
        # 1. Resolve and validate workspace boundary security
        resolved_path = self.guard.resolve_workspace_path(doc_path)
        self.guard.validate_file_access(resolved_path)

        file_stat = resolved_path.stat()
        file_size = file_stat.st_size
        suffix = resolved_path.suffix.lower()
        title = resolved_path.name

        paragraphs: List[str] = []
        tables: List[List[List[str]]] = []
        charts: List[Dict[str, Any]] = []
        page_count: int = 1
        line_count: int = 0
        ast_symbols: Optional[Dict[str, Any]] = None
        summary: str = ""

        # Format label mapping
        fmt_label = suffix.lstrip(".").upper() or "TXT"

        logger.info(
            "analyzing_document",
            file_name=title,
            format=fmt_label,
            size_bytes=file_size,
        )

        # 2. Branch by extension for genuine extraction
        if suffix in (".md", ".markdown", ".txt", ".log", ".sql", ".sh", ".bat", ".ps1", ".env.example", ".html", ".css", ".ts", ".js", ".tsx", ".jsx"):
            paragraphs, tables, line_count, summary = self._extract_text_and_markdown(resolved_path, fmt_label)
            page_count = max(1, (line_count + 49) // 50)

        elif suffix == ".py":
            paragraphs, tables, ast_symbols, line_count, summary = self._extract_python_ast(resolved_path)
            page_count = max(1, (line_count + 49) // 50)

        elif suffix == ".csv":
            paragraphs, tables, line_count, summary = self._extract_csv(resolved_path)
            page_count = 1

        elif suffix in (".json", ".toml", ".yaml", ".yml"):
            paragraphs, tables, line_count, summary = self._extract_structured_config(resolved_path, fmt_label)
            page_count = max(1, (line_count + 49) // 50)

        elif suffix == ".pdf":
            paragraphs, tables, page_count, line_count, summary = self._extract_pdf(resolved_path)

        elif suffix == ".docx":
            paragraphs, tables, page_count, line_count, summary = self._extract_docx(resolved_path)

        else:
            raise ValueError(f"Unsupported document format: '{suffix}'")

        return DocumentAnalysis(
            doc_path=str(resolved_path),
            title=title,
            page_count=page_count,
            format=fmt_label,
            paragraphs=paragraphs,
            tables=tables,
            charts=charts,
            summary=summary,
            line_count=line_count,
            size_bytes=file_size,
            ast_symbols=ast_symbols,
        )

    # =========================================================================
    # 1. Plain Text and Markdown Extractor
    # =========================================================================
    def _extract_text_and_markdown(self, path: Path, fmt: str) -> Tuple[List[str], List[List[List[str]]], int, str]:
        raw_text = self._read_file_text_safely(path)
        lines = raw_text.splitlines()
        line_count = len(lines)

        # Extract paragraphs (blocks separated by blank lines)
        raw_blocks = re.split(r"\n\s*\n", raw_text)
        paragraphs = [b.strip() for b in raw_blocks if b.strip()]

        # Extract markdown tables if present
        tables: List[List[List[str]]] = []
        current_table: List[List[str]] = []
        in_table = False

        for line in lines:
            trimmed = line.strip()
            if trimmed.startswith("|") and trimmed.endswith("|"):
                # Table row
                parts = [c.strip() for c in trimmed.split("|")[1:-1]]
                if all(re.match(r"^:?-+:?$", p) for p in parts if p):
                    # Separator line, skip header divider
                    continue
                current_table.append(parts)
                in_table = True
            else:
                if in_table and current_table:
                    tables.append(current_table)
                    current_table = []
                in_table = False

        if current_table:
            tables.append(current_table)

        summary = f"Parsed {fmt} document '{path.name}' ({line_count} lines, {len(paragraphs)} paragraph blocks, {len(tables)} tables)."
        return paragraphs, tables, line_count, summary

    # =========================================================================
    # 2. Python Source and AST Extractor
    # =========================================================================
    def _extract_python_ast(self, path: Path) -> Tuple[List[str], List[List[List[str]]], Dict[str, Any], int, str]:
        raw_code = self._read_file_text_safely(path)
        lines = raw_code.splitlines()
        line_count = len(lines)

        classes: List[Dict[str, Any]] = []
        functions: List[Dict[str, Any]] = []
        imports: List[str] = []
        docstring: Optional[str] = None

        try:
            tree = ast.parse(raw_code, filename=str(path))
            docstring = ast.get_docstring(tree)

            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": methods,
                        "docstring": ast.get_docstring(node),
                    })
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "args": [a.arg for a in node.args.args],
                        "docstring": ast.get_docstring(node),
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ""
                    for alias in node.names:
                        imports.append(f"{mod}.{alias.name}" if mod else alias.name)

        except SyntaxError as e:
            logger.warning("python_ast_parse_syntax_error", path=str(path), error=str(e))
            docstring = f"Syntax error parsing AST: {e}"

        ast_symbols = {
            "classes": classes,
            "functions": functions,
            "imports": imports,
            "module_docstring": docstring,
        }

        # Format descriptive paragraphs from AST
        paragraphs = []
        if docstring:
            paragraphs.append(f"Module Docstring: {docstring}")
        if imports:
            paragraphs.append(f"Imports ({len(imports)}): {', '.join(imports[:15])}")
        for cls in classes:
            paragraphs.append(f"Class `{cls['name']}` (line {cls['line']}): Methods = {', '.join(cls['methods'])}")
        for fn in functions:
            async_pfx = "async " if fn["is_async"] else ""
            paragraphs.append(f"Function `{async_pfx}{fn['name']}({', '.join(fn['args'])})` (line {fn['line']})")

        # Represent classes/functions as a summary table
        tables: List[List[List[str]]] = []
        if functions or classes:
            table_rows = [["Type", "Name", "Line", "Details"]]
            for c in classes:
                table_rows.append(["Class", c["name"], str(c["line"]), f"{len(c['methods'])} methods"])
            for f in functions:
                table_rows.append(["Function", f["name"], str(f["line"]), f"args: {', '.join(f['args'])}"])
            tables.append(table_rows)

        summary = f"Parsed Python source '{path.name}' ({line_count} lines, {len(classes)} classes, {len(functions)} functions, {len(imports)} imports)."
        return paragraphs, tables, ast_symbols, line_count, summary

    # =========================================================================
    # 3. CSV Tabular Extractor
    # =========================================================================
    def _extract_csv(self, path: Path) -> Tuple[List[str], List[List[List[str]]], int, str]:
        raw_text = self._read_file_text_safely(path)
        lines = raw_text.splitlines()
        line_count = len(lines)

        rows: List[List[str]] = []
        try:
            reader = csv.reader(lines)
            for r in reader:
                if r:
                    rows.append(r)
        except Exception as e:
            logger.warning("csv_parse_error", path=str(path), error=str(e))
            rows = [[line] for line in lines if line.strip()]

        headers = rows[0] if rows else []
        row_count = len(rows) - 1 if len(rows) > 1 else len(rows)

        paragraphs = [
            f"CSV Document '{path.name}': {row_count} data rows, {len(headers)} columns.",
            f"Columns: {', '.join(headers)}" if headers else "No header columns detected.",
        ]

        # Present first 50 rows in tables
        tables = [rows[:50]] if rows else []
        summary = f"Parsed CSV dataset '{path.name}' ({row_count} rows, {len(headers)} columns: {', '.join(headers[:6])})."
        return paragraphs, tables, line_count, summary

    # =========================================================================
    # 4. Structured JSON / TOML / YAML Extractor
    # =========================================================================
    def _extract_structured_config(self, path: Path, fmt: str) -> Tuple[List[str], List[List[List[str]]], int, str]:
        raw_text = self._read_file_text_safely(path)
        lines = raw_text.splitlines()
        line_count = len(lines)

        paragraphs = []
        tables = []

        if fmt == "JSON":
            try:
                data = json.loads(raw_text)
                if isinstance(data, dict):
                    keys = list(data.keys())
                    paragraphs.append(f"JSON Object containing {len(keys)} top-level keys: {', '.join(keys)}")
                    table_rows = [["Key", "Type", "Sample Value"]]
                    for k in keys[:25]:
                        val = data[k]
                        val_str = str(val)[:40] + "..." if len(str(val)) > 40 else str(val)
                        table_rows.append([str(k), type(val).__name__, val_str])
                    tables.append(table_rows)
                elif isinstance(data, list):
                    paragraphs.append(f"JSON Array containing {len(data)} items.")
            except json.JSONDecodeError as e:
                paragraphs.append(f"Malformed JSON: {e}")
        else:
            # TOML or YAML lines
            paragraphs.append(f"{fmt} Configuration file '{path.name}' containing {line_count} lines.")
            for line in lines[:30]:
                if line.strip() and not line.strip().startswith("#"):
                    paragraphs.append(line.strip())

        summary = f"Parsed {fmt} configuration '{path.name}' ({line_count} lines)."
        return paragraphs, tables, line_count, summary

    # =========================================================================
    # 5. PDF Document Extractor
    # =========================================================================
    def _extract_pdf(self, path: Path) -> Tuple[List[str], List[List[List[str]]], int, int, str]:
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            page_count = len(reader.pages)
            paragraphs: List[str] = []
            tables: List[List[List[str]]] = []
            total_chars = 0

            # Extract metadata
            if reader.metadata:
                meta = reader.metadata
                meta_items = []
                if meta.title:
                    meta_items.append(f"Title: {meta.title}")
                if meta.author:
                    meta_items.append(f"Author: {meta.author}")
                if meta_items:
                    paragraphs.append(" | ".join(meta_items))

            # Extract text per page
            for idx, page in enumerate(reader.pages, 1):
                page_text = page.extract_text() or ""
                cleaned = page_text.strip()
                if cleaned:
                    total_chars += len(cleaned)
                    # Split page into paragraphs
                    blocks = [b.strip() for b in re.split(r"\n\s*\n", cleaned) if b.strip()]
                    if len(blocks) > 1:
                        for blk in blocks:
                            paragraphs.append(f"[Page {idx}] {blk}")
                    else:
                        for line in cleaned.splitlines():
                            l_str = line.strip()
                            if l_str:
                                paragraphs.append(l_str)

                    # Detect tabular text rows
                    current_table: List[List[str]] = []
                    for line in page_text.splitlines():
                        line_str = line.strip()
                        if not line_str:
                            if len(current_table) >= 2:
                                tables.append(current_table)
                                current_table = []
                            continue
                        if "|" in line_str:
                            cells = [c.strip() for c in line_str.split("|") if c.strip()]
                            if len(cells) >= 2:
                                current_table.append(cells)
                        elif "\t" in line_str:
                            cells = [c.strip() for c in line_str.split("\t") if c.strip()]
                            if len(cells) >= 2:
                                current_table.append(cells)
                    if len(current_table) >= 2:
                        tables.append(current_table)

            line_count = len(paragraphs)
            summary = f"Parsed PDF document '{path.name}' ({page_count} pages, {len(paragraphs)} text blocks, {len(tables)} tables, {total_chars} characters)."
            return paragraphs, tables, page_count, line_count, summary

        except Exception as e:
            logger.error("pdf_extraction_failure", path=str(path), error=str(e))
            raise ValueError(f"Failed to extract PDF contents from '{path.name}': {e}")

    # =========================================================================
    # 6. DOCX Document Extractor
    # =========================================================================
    def _extract_docx(self, path: Path) -> Tuple[List[str], List[List[List[str]]], int, int, str]:
        try:
            from docx import Document
            doc = Document(str(path))
            paragraphs: List[str] = []

            for p in doc.paragraphs:
                txt = p.text.strip()
                if txt:
                    paragraphs.append(txt)

            tables: List[List[List[str]]] = []
            for t in doc.tables:
                t_matrix: List[List[str]] = []
                for row in t.rows:
                    row_cells = [cell.text.strip() for cell in row.cells]
                    t_matrix.append(row_cells)
                if t_matrix:
                    tables.append(t_matrix)

            line_count = len(paragraphs)
            page_count = max(1, (line_count + 39) // 40)
            summary = f"Parsed DOCX document '{path.name}' ({len(paragraphs)} paragraphs, {len(tables)} tables)."
            return paragraphs, tables, page_count, line_count, summary

        except Exception as e:
            logger.error("docx_extraction_failure", path=str(path), error=str(e))
            raise ValueError(f"Failed to extract DOCX contents from '{path.name}': {e}")

    # =========================================================================
    # Helper: Safe UTF-8 with Latin-1 Fallback Reader
    # =========================================================================
    def _read_file_text_safely(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                return path.read_text(encoding="latin-1")
            except Exception as e:
                raise ValueError(f"Unable to decode text file '{path.name}': {e}")
