"""Core RefactoringEngine coordinating planners, snapshots, validation checks, and rollbacks.
"""

import hashlib
import json
import os
import time
from typing import Any, List, Optional

from app.agents.software_engineer.refactoring.cache import RefactoringCache
from app.agents.software_engineer.refactoring.conflict_detector import WorkspaceConflictDetector
from app.agents.software_engineer.refactoring.context_builder import RepositoryContextBuilder
from app.agents.software_engineer.refactoring.diff_generator import WorkspaceDiffGenerator
from app.agents.software_engineer.generator.exceptions import ModelGenerationError
from app.agents.software_engineer.refactoring.exceptions import (
    RefactoringError,
    ValidationFailureError,
)
from app.agents.software_engineer.refactoring.formatter import RefactoringCodeFormatter
from app.agents.software_engineer.refactoring.interfaces import RefactoringEngine
from app.agents.software_engineer.refactoring.models import (
    ConflictReport,
    DiffReport,
    PatchReport,
    RefactoringPreview,
    RefactoringRequest,
    RefactoringResult,
    RefactoringStatistics,
)
from app.agents.software_engineer.refactoring.patch_generator import WorkspacePatchGenerator
from app.agents.software_engineer.refactoring.planner import WorkspaceRefactoringPlanner
from app.agents.software_engineer.refactoring.prompt_builder import RefactoringPromptBuilder
from app.agents.software_engineer.refactoring.rollback import WorkspaceRollbackManager
from app.agents.software_engineer.refactoring.snapshot import WorkspaceSnapshotManager
from app.agents.software_engineer.refactoring.validator import CodeValidator
from app.agents.software_engineer.generator.utils import extract_code_block
from app.ai.models import ChatRequest


class LocalRefactoringEngine(RefactoringEngine):
    """Executes code refactor pipelines with safety snapshot backups and rollbacks."""

    def __init__(self, gateway: Any, workspace_root: Optional[str] = None) -> None:
        """Initializes LocalRefactoringEngine.

        Args:
            gateway: Active AI Gateway.
            workspace_root: Workspace root path.
        """
        self.gateway = gateway
        self.workspace_root = workspace_root or os.getcwd()

        self.planner = WorkspaceRefactoringPlanner()
        self.context_builder = RepositoryContextBuilder()
        self.prompt_builder = RefactoringPromptBuilder()
        self.conflict_detector = WorkspaceConflictDetector()
        self.snapshot_manager = WorkspaceSnapshotManager(self.workspace_root)
        self.rollback_manager = WorkspaceRollbackManager(self.workspace_root)
        self.validator = CodeValidator()
        self.formatter = RefactoringCodeFormatter()
        self.diff_generator = WorkspaceDiffGenerator()
        self.patch_generator = WorkspacePatchGenerator()

        # Cache setup
        cache_path = os.path.join(self.workspace_root, ".nova", "refactoring_cache.json")
        self.cache = RefactoringCache(cache_path)

    def _resolve_model(self, request: RefactoringRequest) -> str:
        model_name = request.model_override
        if not model_name and hasattr(self.gateway, "model_registry"):
            model_name = self.gateway.model_registry.default_model()
        return model_name or "llama3"

    async def execute_refactoring(self, request: RefactoringRequest) -> RefactoringResult:
        """Runs the refactoring operation inside safety pipeline wrapper context.

        Args:
            request: RefactoringRequest parameter details.

        Returns:
            RefactoringResult reports.
        """
        start_time = time.perf_counter()
        target_file = request.file_path or "refactored_code.py"
        abs_target_path = os.path.join(self.workspace_root, target_file)

        # 1. Build Context and identify naming/imports style profiles
        context = self.context_builder.build_context(request, self.workspace_root)
        context_hash = hashlib.sha256(
            json.dumps(context.model_dump()).encode("utf-8")
        ).hexdigest()

        # 2. Decompose plan steps
        plan = self.planner.plan_refactoring(request, context)

        # 3. Conflict pre-scan checks
        conflicts = self.conflict_detector.detect_conflicts(self.workspace_root, plan)
        if conflicts.has_conflict:
            duration = time.perf_counter() - start_time
            return RefactoringResult(
                success=False,
                statistics=RefactoringStatistics(
                    duration=duration,
                    affected_files_count=0,
                    validation_status="conflict_detected",
                    model_used=self._resolve_model(request),
                ),
            )

        # 4. Take Snapshot backup before filesystem updates
        snapshot = self.snapshot_manager.create_snapshot(self.workspace_root, [target_file])

        # 5. Read original content
        original_content = ""
        if os.path.exists(abs_target_path):
            with open(abs_target_path, "r", encoding="utf-8") as f:
                original_content = f.read()

        # 6. Check cache hits
        cached = self.cache.get(request.prompt, context_hash)
        model_name = self._resolve_model(request)

        if cached:
            modified_content = cached
        else:
            # 7. Model prompts compile and AI Gateway execution
            prompt_pkg = self.prompt_builder.build_prompt(request, context, request.prompt)
            chat_req = ChatRequest(
                messages=prompt_pkg.messages,
                model=model_name,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            try:
                chat_res = await self.gateway.chat(chat_req)
                raw_out = chat_res.message.content
            except Exception as e:
                # Cleanup and raise
                raise ModelGenerationError(f"Local model generation invocation failed: {str(e)}") from e

            modified_content = extract_code_block(raw_out, "python")

        # 8. Formatter spacing alignment
        from app.agents.software_engineer.generator.models import StyleProfile
        style_profile = StyleProfile.model_validate(context.style_guidelines)
        fmt_res = self.formatter.format_code(modified_content, style_profile)
        final_content = fmt_res.content if fmt_res.success else modified_content

        # 9. Validation compile testing
        validation = self.validator.validate_code(target_file, final_content)

        if not validation.is_valid:
            # Revert using snapshot rollback
            rollback_res = self.rollback_manager.rollback(snapshot.snapshot_id)
            duration = time.perf_counter() - start_time
            raise ValidationFailureError(
                f"Generated code failed compile check: {validation.errors}. Rollback succeeded: {rollback_res.success}"
            )

        # 10. Write final code content to workspace file path
        os.makedirs(os.path.dirname(abs_target_path), exist_ok=True)
        with open(abs_target_path, "w", encoding="utf-8") as f:
            f.write(final_content)

        # Save to cache
        if not cached:
            self.cache.set(request.prompt, context_hash, final_content)
            self.cache.save()

        # 11. Diff and patch compiler
        diff_rep = self.diff_generator.generate_diff(target_file, original_content, final_content)
        patch_rep = self.patch_generator.generate_patch([diff_rep])

        preview = RefactoringPreview(
            plan=plan,
            diffs=[diff_rep],
            conflicts=conflicts,
            estimated_risk=plan.estimated_risk,
            rollback_available=True,
        )

        duration = time.perf_counter() - start_time
        stats = RefactoringStatistics(
            duration=duration,
            affected_files_count=1,
            validation_status="valid",
            model_used=model_name,
        )

        return RefactoringResult(
            success=True,
            snapshot_id=snapshot.snapshot_id,
            preview=preview,
            applied_patches=patch_rep,
            statistics=stats,
        )
