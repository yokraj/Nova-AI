"""Targeted Code Context Manager for Nova-AI's Autonomous Coding Agent.

Provides goal-driven code search (ripgrep/AST symbol search), context minimization,
and working memory tracking of inspected files, symbols, and dependencies.
"""

import os
import re
import ast
import subprocess
from typing import Any, Dict, List, Optional
import structlog

from app.ai.memory.working_memory import WorkingMemoryManager

logger = structlog.get_logger("code_context_manager")


class CodeContextManager:
    """Targeted code context retrieval and memory synchronization manager."""

    def __init__(self, root_dir: str = ".") -> None:
        self.root_dir = os.path.abspath(root_dir)
        self.working_memory = WorkingMemoryManager.get_instance()

    def search_codebase(
        self, query: str, search_type: str = "text", target_dir: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Searches local codebase for text, symbol, function, or class references."""
        root = os.path.abspath(target_dir or self.root_dir)
        results = []

        if search_type == "symbol" or search_type == "function" or search_type == "class":
            # Use AST parsing for Python or regex search for general languages
            results = self._search_symbols(root, query, search_type)
        else:
            # Ripgrep / text search fallback
            results = self._search_text(root, query)

        logger.info("Executed code search", query=query, type=search_type, match_count=len(results))
        return results

    def _search_text(self, root_dir: str, query: str) -> List[Dict[str, Any]]:
        """Performs fast text/regex search using ripgrep or Python walk fallback."""
        results = []
        try:
            cmd = ["rg", "-n", "-i", "--max-columns", "200", query, root_dir]
            res = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if res.returncode == 0:
                for line in res.stdout.splitlines()[:50]:
                    parts = line.split(":", 2)
                    if len(parts) >= 3:
                        rel_file = os.path.relpath(parts[0], root_dir)
                        results.append({
                            "file": rel_file,
                            "line": int(parts[1]) if parts[1].isdigit() else 1,
                            "content": parts[2].strip()
                        })
                return results
        except Exception:
            pass

        # Python fallback search
        q_lower = query.lower()
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", "venv", ".venv", "dist", "build")]
            for f in files:
                if f.endswith((".py", ".ts", ".js", ".java", ".rs", ".go", ".cpp", ".c", ".h", ".json", ".toml")):
                    full_p = os.path.join(root, f)
                    try:
                        with open(full_p, "r", encoding="utf-8", errors="ignore") as fh:
                            for idx, line in enumerate(fh, start=1):
                                if q_lower in line.lower():
                                    rel_f = os.path.relpath(full_p, root_dir)
                                    results.append({
                                        "file": rel_f,
                                        "line": idx,
                                        "content": line.strip()
                                    })
                                    if len(results) >= 50:
                                        return results
                    except Exception:
                        continue
        return results

    def _search_symbols(self, root_dir: str, query: str, search_type: str) -> List[Dict[str, Any]]:
        """Extracts class and function symbols from Python AST files."""
        results = []
        q_lower = query.lower()

        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", "venv", ".venv", "dist", "build")]
            for f in files:
                if f.endswith(".py"):
                    full_p = os.path.join(root, f)
                    try:
                        with open(full_p, "r", encoding="utf-8", errors="ignore") as fh:
                            content = fh.read()
                            parsed = ast.parse(content)
                            for node in ast.walk(parsed):
                                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                                    if q_lower in node.name.lower():
                                        rel_f = os.path.relpath(full_p, root_dir)
                                        kind = "class" if isinstance(node, ast.ClassDef) else "function"
                                        results.append({
                                            "file": rel_f,
                                            "line": node.lineno,
                                            "kind": kind,
                                            "name": node.name,
                                            "content": f"{kind} {node.name}"
                                        })
                    except Exception:
                        continue
        return results

    def build_goal_context(
        self, user_goal: str, target_files: List[str], task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Assembles a minimal targeted code context payload without overloading model tokens."""
        file_contexts = []
        root = self.root_dir

        for rel_f in target_files:
            full_p = os.path.join(root, rel_f) if not os.path.isabs(rel_f) else rel_f
            if os.path.exists(full_p):
                try:
                    with open(full_p, "r", encoding="utf-8", errors="ignore") as fh:
                        lines = fh.readlines()
                        snippet = "".join(lines[:300])  # Cap at first 300 lines per file
                        file_contexts.append({
                            "path": rel_f,
                            "line_count": len(lines),
                            "content_snippet": snippet
                        })
                except Exception as e:
                    logger.debug("Failed to read file for context", path=rel_f, error=str(e))

        context_payload = {
            "user_goal": user_goal,
            "target_files": file_contexts,
            "total_files": len(file_contexts),
        }

        if task_id:
            task = self.working_memory.get_task(task_id)
            if task:
                task.observations.append({"inspected_files": [f["path"] for f in file_contexts]})

        return context_payload
