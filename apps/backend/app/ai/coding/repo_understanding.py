"""Universal Repository Understanding Engine for Nova-AI's Autonomous Coding Agent.

Autonomously inspects local filesystem directories to detect project types, primary languages,
frameworks, entry points, dependency manifests, build systems, test suites, and Git state.
"""

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger("repo_understanding")


class RepoUnderstandingEngine:
    """Real physical repository inspection engine for multi-language local projects."""

    PROJECT_INDICATORS = {
        "Python": ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile"],
        "JavaScript/TypeScript": ["package.json", "tsconfig.json", "vite.config.ts", "next.config.js"],
        "Java": ["pom.xml", "build.gradle", "build.gradle.kts"],
        "C/C++": ["CMakeLists.txt", "Makefile", "configure.ac"],
        "Rust": ["Cargo.toml"],
        "Go": ["go.mod"],
    }

    TEST_INDICATORS = {
        "pytest": ["pytest.ini", "tests", "test_*.py"],
        "jest/vitest": ["jest.config.js", "vitest.config.ts"],
        "maven/gradle": ["src/test"],
        "cargo_test": ["tests"],
        "go_test": ["*_test.go"],
    }

    def __init__(self, root_path: str = ".") -> None:
        self.root_path = os.path.abspath(root_path)

    def analyze_repository(self, project_dir: Optional[str] = None) -> Dict[str, Any]:
        """Scans host directory and returns empirical project understanding metadata."""
        target_dir = os.path.abspath(project_dir or self.root_path)

        if not os.path.exists(target_dir):
            raise FileNotFoundError(f"Project directory '{target_dir}' does not exist.")

        detected_languages = []
        detected_manifests = []
        entry_points = []
        source_dirs = []

        # 1. Inspect manifests and indicator files
        for lang, indicators in self.PROJECT_INDICATORS.items():
            for ind in indicators:
                full_ind = os.path.join(target_dir, ind)
                if os.path.exists(full_ind):
                    if lang not in detected_languages:
                        detected_languages.append(lang)
                    detected_manifests.append(ind)

        # 2. Directory structure scanning
        entries = os.listdir(target_dir)
        for item in entries:
            item_path = os.path.join(target_dir, item)
            if os.path.isdir(item_path) and not item.startswith(".") and item not in ("node_modules", "__pycache__", "venv", ".venv", "dist", "build"):
                source_dirs.append(item)
                # Look for entry points
                for candidate in ("main.py", "app.py", "index.ts", "index.js", "main.rs", "main.go", "App.tsx", "App.jsx"):
                    if os.path.exists(os.path.join(item_path, candidate)):
                        entry_points.append(os.path.relpath(os.path.join(item_path, candidate), target_dir))

        # Root entry point check
        for candidate in ("main.py", "app.py", "index.js", "index.ts", "main.rs", "main.go", "server.js"):
            candidate_path = os.path.join(target_dir, candidate)
            if os.path.exists(candidate_path):
                rel_p = os.path.relpath(candidate_path, target_dir)
                if rel_p not in entry_points:
                    entry_points.append(rel_p)

        # 3. Git Status Inspection
        git_state = self.inspect_git_state(target_dir)

        # 4. Count lines of code & file summary
        file_summary = self._summarize_files(target_dir)

        project_type = detected_languages[0] if detected_languages else "Generic Text/Script"

        understanding = {
            "project_path": target_dir,
            "project_type": project_type,
            "languages": detected_languages or ["Unknown"],
            "manifest_files": detected_manifests,
            "entry_points": entry_points or ["None detected"],
            "source_directories": source_dirs,
            "git_state": git_state,
            "file_counts": file_summary["counts"],
            "total_files": file_summary["total_files"],
        }
        logger.info("Analyzed repository structure", path=target_dir, type=project_type, languages=detected_languages)
        return understanding

    def inspect_git_state(self, target_dir: str) -> Dict[str, Any]:
        """Retrieves actual Git repository state (branch, modified files, status)."""
        git_dir = os.path.join(target_dir, ".git")
        if not os.path.exists(git_dir):
            return {"is_git_repo": False, "branch": "none", "modified_files": [], "untracked_files": []}

        try:
            branch_out = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=target_dir, capture_output=True, text=True, check=False)
            branch = branch_out.stdout.strip() if branch_out.returncode == 0 else "unknown"

            status_out = subprocess.run(["git", "status", "--porcelain"], cwd=target_dir, capture_output=True, text=True, check=False)
            modified = []
            untracked = []
            if status_out.returncode == 0:
                for line in status_out.stdout.splitlines():
                    if line.startswith(" M") or line.startswith("M "):
                        modified.append(line[3:].strip())
                    elif line.startswith("??"):
                        untracked.append(line[3:].strip())

            return {
                "is_git_repo": True,
                "branch": branch,
                "modified_files": modified,
                "untracked_files": untracked,
            }
        except Exception as e:
            logger.debug("Failed to inspect git state", error=str(e))
            return {"is_git_repo": True, "branch": "unknown", "error": str(e)}

    def _summarize_files(self, target_dir: str) -> Dict[str, Any]:
        """Counts files by extension in target directory."""
        counts: Dict[str, int] = {}
        total = 0
        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", "venv", ".venv", "dist", "build", "coverage")]
            for f in files:
                total += 1
                ext = os.path.splitext(f)[1].lower() or "no_ext"
                counts[ext] = counts.get(ext, 0) + 1
        return {"counts": counts, "total_files": total}
