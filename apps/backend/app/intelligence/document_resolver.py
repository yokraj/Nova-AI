"""Document Context Resolver for Grounded Inference in Nova AI (Vertical 1).

Connects natural language user queries referencing files to the DocumentIntelligence
engine and WorkspaceSecurityGuard:
1. Detects candidate file paths in prompt.
2. Enforces workspace boundary sandboxing (blocking traversal and unauthorized absolute paths).
3. Analyzes genuine file contents (TXT, MD, PY, JSON, CSV, PDF, DOCX).
4. Formats an authoritative Grounded Document Context to inject into the LLM context.
5. Emits strict security violations and honest missing-file errors without hallucination.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import structlog

from app.ai.research.document_intelligence import DocumentIntelligence
from app.ai.research.models import DocumentAnalysis
from app.security.workspace_guard import (
    WorkspaceSecurityGuard,
    WorkspaceSecurityException,
)

logger = structlog.get_logger("document_resolver")


class DocumentContextResolver:
    """Detects and resolves referenced workspace files into authoritative grounding context."""

    def __init__(
        self,
        guard: Optional[WorkspaceSecurityGuard] = None,
        doc_intel: Optional[DocumentIntelligence] = None,
    ) -> None:
        self.guard = guard or WorkspaceSecurityGuard()
        self.doc_intel = doc_intel or DocumentIntelligence(self.guard)

    async def resolve_document_grounding(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Inspects prompt for file references and returns grounding payload or security/file error.

        Returns:
            Dict containing either:
            - 'grounded_prompt_prefix': Formatted grounding text to prepend to LLM prompt.
            - 'grounded_system_prompt': Grounding instructions for system prompt.
            - 'source_file': Name/path of inspected file.
            - 'analysis': Full DocumentAnalysis instance.
            OR:
            - 'security_error': Description if unauthorized path traversal was attempted.
            - 'missing_file_error': Description if explicitly referenced file is not found.
            OR:
            - None if no file is referenced.
        """
        candidates = self.guard.extract_file_references(prompt)
        if not candidates:
            return None

        # Inspect first matching candidate
        cand = candidates[0]

        # 1. Check workspace security containment
        try:
            resolved = self.guard.resolve_workspace_path(cand)
        except WorkspaceSecurityException as e:
            logger.warning("file_grounding_security_violation", candidate=cand, error=str(e))
            return {
                "security_error": f"Security Error: Access Denied. Path '{cand}' is outside the authorized workspace boundary '{self.guard.root_dir}'."
            }
        except ValueError as e:
            return {
                "security_error": f"Security Error: Invalid path '{cand}': {e}"
            }

        # 2. Check existence
        if not resolved.exists():
            # If user explicitly asked for file (e.g. "read", "summarize", "check", "in", "file")
            prompt_lower = prompt.lower()
            is_explicit_file_query = any(k in prompt_lower for k in ["read", "summarize", "explain", "check", "file", "open", "in ", "look at", "what is in"])
            if is_explicit_file_query:
                return {
                    "missing_file_error": f"File Error: Unable to locate file '{cand}' within authorized workspace '{self.guard.root_dir}'."
                }
            return None

        if not resolved.is_file():
            return None

        # 3. Analyze real document
        try:
            analysis: DocumentAnalysis = await self.doc_intel.analyze_document(str(resolved))
        except Exception as e:
            logger.error("document_grounding_analysis_failed", path=str(resolved), error=str(e))
            return {
                "analysis_error": f"Document Processing Error: Failed to parse '{cand}': {e}"
            }

        # 4. Format Authoritative Grounded Document Context
        context_lines: List[str] = [
            f"[AUTHENTIC WORKSPACE DOCUMENT: {analysis.title}]",
            f"File Path: {resolved.relative_to(self.guard.root_dir)}",
            f"Format: {analysis.format} | Lines: {analysis.line_count} | Size: {analysis.size_bytes} bytes | Pages: {analysis.page_count}",
            f"File Summary: {analysis.summary}",
        ]

        # Add AST symbol summary if present
        if analysis.ast_symbols:
            syms = analysis.ast_symbols
            if syms.get("module_docstring"):
                context_lines.append(f"Module Docstring: {syms['module_docstring']}")
            if syms.get("imports"):
                context_lines.append(f"Imports: {', '.join(syms['imports'][:15])}")
            if syms.get("classes"):
                cls_names = [f"`{c['name']}` (line {c['line']}, methods: {', '.join(c['methods'])})" for c in syms["classes"]]
                context_lines.append(f"Classes: {'; '.join(cls_names)}")
            if syms.get("functions"):
                fn_names = [f"`{fn['name']}({', '.join(fn['args'])})` (line {fn['line']})" for fn in syms["functions"]]
                context_lines.append(f"Functions: {'; '.join(fn_names)}")

        # Add Tables if present
        if analysis.tables:
            context_lines.append("\nExtracted Tabular Data:")
            for t_idx, table in enumerate(analysis.tables[:3], 1):
                context_lines.append(f"Table #{t_idx}:")
                for row in table[:15]:
                    context_lines.append("  | " + " | ".join(row) + " |")

        # Add Paragraphs / Content blocks
        context_lines.append("\nExtracted Document Content:")
        for p in analysis.paragraphs[:25]:
            context_lines.append(p)

        context_lines.append("[END OF AUTHENTIC WORKSPACE DOCUMENT]\n")

        grounded_prefix = "\n".join(context_lines)
        system_instruction = (
            "You are Nova AI operating assistant. You have been provided with an authentic, verified "
            "workspace document above. Answer the user's inquiry based strictly and faithfully on this "
            "document. Cite the source file name, specific lines, functions, classes, tables, or sections. "
            "Never hallucinate or assume contents not present in the document."
        )

        return {
            "source_file": analysis.title,
            "relative_path": str(resolved.relative_to(self.guard.root_dir)),
            "format": analysis.format,
            "line_count": analysis.line_count,
            "grounded_prefix": grounded_prefix,
            "system_instruction": system_instruction,
            "analysis": analysis,
        }

