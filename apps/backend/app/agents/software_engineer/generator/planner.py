"""Decomposes coding requests into step-by-step Generation Plans.
"""

from app.agents.software_engineer.generator.interfaces import GenerationPlanner
from app.agents.software_engineer.generator.models import (
    GenerationContext,
    GenerationPlan,
    GenerationRequest,
    GenerationTask,
)


class WorkspaceGenerationPlanner(GenerationPlanner):
    """Parses generation directives compiling task sequences."""

    def plan_generation(
        self, request: GenerationRequest, context: GenerationContext
    ) -> GenerationPlan:
        """Determines files to create/modify and maps dependencies between tasks.

        Args:
            request: Code generation request.
            context: Collected context.

        Returns:
            GenerationPlan model.
        """
        # Determine target file path
        target_path = request.file_path or "generated_code.py"

        # Check if prompt requests multiple files, e.g. "FastAPI routes and schemas"
        prompt_lower = request.prompt.lower()
        tasks = []

        if "routes" in prompt_lower and "schema" in prompt_lower:
            # Multi-file decomposition
            base_dir = os.path.dirname(target_path) or "."
            schema_file = os.path.join(base_dir, "schemas.py")
            routes_file = os.path.join(base_dir, "routes.py")

            task_schema = GenerationTask(
                id="task-schema",
                file_path=schema_file,
                instructions=f"Generate Pydantic validation schemas based on: {request.prompt}",
                dependencies=[],
            )
            task_routes = GenerationTask(
                id="task-routes",
                file_path=routes_file,
                instructions=f"Generate FastAPI endpoint router utilizing schemas in 'schemas.py': {request.prompt}",
                dependencies=["task-schema"],
            )
            tasks.extend([task_schema, task_routes])
        else:
            # Single file plan
            tasks.append(
                GenerationTask(
                    id="task-1",
                    file_path=target_path,
                    instructions=request.prompt,
                    dependencies=[],
                )
            )

        return GenerationPlan(
            plan_id=f"plan-{int(time.time())}",
            request_summary=request.prompt[:100],
            tasks=tasks,
        )


import os
import time
