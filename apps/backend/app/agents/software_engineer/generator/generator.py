"""Main CodeGenerator coordinating plans, prompts context and code validations.
"""

import hashlib
import time
from typing import Any, Dict, List, Optional

from app.agents.software_engineer.generator.cache import GenerationCache
from app.agents.software_engineer.generator.code_validator import GeneratedCodeValidator
from app.agents.software_engineer.generator.context_builder import RepositoryContextBuilder
from app.agents.software_engineer.generator.exceptions import CodeGenerationError, ModelGenerationError
from app.agents.software_engineer.generator.formatter import SourceCodeFormatter
from app.agents.software_engineer.generator.interfaces import CodeGenerator
from app.agents.software_engineer.generator.models import (
    GeneratedFile,
    GenerationPlan,
    GenerationRequest,
    GenerationResult,
    GenerationStatistics,
)
from app.agents.software_engineer.generator.planner import WorkspaceGenerationPlanner
from app.agents.software_engineer.generator.post_processor import CodePostProcessor
from app.agents.software_engineer.generator.prompt_builder import CodePromptBuilder
from app.agents.software_engineer.generator.utils import extract_code_block
from app.ai.models import ChatRequest


class LocalCodeGenerator(CodeGenerator):
    """Orchestrates generation tasks invoking Ollama models through central AI Gateway."""

    def __init__(self, gateway: Any, workspace_root: Optional[str] = None) -> None:
        """Initializes LocalCodeGenerator.

        Args:
            gateway: Active AIGateway instance.
            workspace_root: Workspace root path.
        """
        self.gateway = gateway
        self.workspace_root = workspace_root
        self.planner = WorkspaceGenerationPlanner()
        self.context_builder = RepositoryContextBuilder()
        self.prompt_builder = CodePromptBuilder()
        self.validator = GeneratedCodeValidator()
        self.formatter = SourceCodeFormatter()
        self.post_processor = CodePostProcessor()

        # Cache setup
        cache_path = None
        if workspace_root:
            cache_path = os.path.join(workspace_root, ".nova", "generation_cache.json")
            self.cache = GenerationCache(cache_path)
        else:
            self.cache = None

    def _resolve_model(self, request: GenerationRequest) -> str:
        """Dynamically identifies active local coding model name."""
        model_name = request.model_override
        if not model_name and hasattr(self.gateway, "model_registry"):
            model_name = self.gateway.model_registry.default_model()
        return model_name or "llama3"

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Executes full generation workflow pipeline.

        Args:
            request: Configuration guidelines request.

        Returns:
            GenerationResult payload report.
        """
        start_time = time.perf_counter()
        workspace = self.workspace_root or os.getcwd()

        # 1. Build Context
        context = self.context_builder.build_context(request, workspace)
        context_hash = hashlib.sha256(
            json.dumps(context.summary.model_dump()).encode("utf-8")
        ).hexdigest()

        # 2. Decompose Plan
        plan = self.planner.plan_generation(request, context)

        # 3. Cache lookup check
        if self.cache:
            cached_output = self.cache.get(request.prompt, context_hash)
            if cached_output:
                # Post process and return cache hit
                processed = self.post_processor.post_process(
                    request.file_path or "generated_code.py", cached_output
                )
                duration = time.perf_counter() - start_time
                return GenerationResult(
                    success=True,
                    plan=plan,
                    files=[processed],
                    statistics=GenerationStatistics(
                        duration=duration,
                        model=self._resolve_model(request),
                        validation_status="skipped_cache",
                    ),
                    cache_hit=True,
                )

        # 4. Process Plan Tasks
        model_name = self._resolve_model(request)
        generated_files: List[GeneratedFile] = []
        prompt_tokens = 0
        completion_tokens = 0

        for task in plan.tasks:
            # 5. Build prompt
            prompt_pkg = self.prompt_builder.build_prompt(request, context, task.instructions)

            # 6. Invoke AI Gateway
            chat_req = ChatRequest(
                messages=prompt_pkg.messages,
                model=model_name,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            try:
                chat_res = await self.gateway.chat(chat_req)
                raw_code = chat_res.message.content
                # Update tokens usage statistics
                if hasattr(chat_res, "usage") and chat_res.usage:
                    prompt_tokens += chat_res.usage.prompt_tokens
                    completion_tokens += chat_res.usage.completion_tokens
            except Exception as e:
                raise ModelGenerationError(f"Local model generation invocation failed: {str(e)}") from e

            # 7. Extract raw code from response markdown wrapper block
            clean_code = extract_code_block(raw_code, request.language)

            # 8. Validate syntax
            validation = self.validator.validate_code(task.file_path, clean_code)

            # 9. Style formatting adjustments
            fmt_res = self.formatter.format_code(clean_code, context.style_profile)
            final_code = fmt_res.content if fmt_res.success else clean_code

            # 10. Post process to compile symbol listings
            file_report = self.post_processor.post_process(task.file_path, final_code)
            generated_files.append(file_report)

            # Set in cache
            if self.cache:
                self.cache.set(request.prompt, context_hash, final_code, model_name)

        if self.cache:
            self.cache.save()

        duration = time.perf_counter() - start_time
        stats = GenerationStatistics(
            duration=duration,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            model=model_name,
            validation_status="valid" if all(validation.is_valid for _ in range(1)) else "invalid",
        )

        return GenerationResult(
            success=True,
            plan=plan,
            files=generated_files,
            statistics=stats,
            cache_hit=False,
        )


import json
import os
