"""Workflow Builder generates execution step graphs matching target prompts.
"""

from app.agents.software_engineer.autonomous.interfaces import IWorkflowBuilder
from app.agents.software_engineer.autonomous.models import AutonomousRequest, ExecutionContext, Workflow, WorkflowStep

class LocalWorkflowBuilder(IWorkflowBuilder):
    """Parses prompts to build sequential lists of capability steps."""

    def build_workflow(self, request: AutonomousRequest, context: ExecutionContext) -> Workflow:
        """Returns ordered steps for code operations, refactoring, testing, and deployments."""
        prompt = request.prompt.lower()
        steps = []

        # 1. Base analysis step
        steps.append(WorkflowStep(
            id="step-analysis",
            name="Workspace Codebase Analysis",
            target_engine="Code Intelligence Engine"
        ))

        # 2. Add modules or specs planning
        if "project" in prompt or "create" in prompt or "platform" in prompt or "build" in prompt:
            steps.append(WorkflowStep(
                id="step-project-plan",
                name="System Requirements and Sprint Planning",
                target_engine="Project Manager Engine",
                dependencies=["step-analysis"]
            ))

        # 3. Code creation/fixing/refactoring step
        if "fix" in prompt or "error" in prompt or "debug" in prompt:
            steps.append(WorkflowStep(
                id="step-debugging",
                name="Locate and Repair Code Error",
                target_engine="Debugging Engine",
                dependencies=["step-analysis"]
            ))
        elif "refactor" in prompt:
            steps.append(WorkflowStep(
                id="step-refactoring",
                name="Perform System Code Refactoring",
                target_engine="Refactoring Engine",
                dependencies=["step-analysis"]
            ))
        else:
            prev = "step-project-plan" if "step-project-plan" in [s.id for s in steps] else "step-analysis"
            steps.append(WorkflowStep(
                id="step-generation",
                name="Autonomous Source Code Generation",
                target_engine="Code Generation Engine",
                dependencies=[prev]
            ))

        # 4. Testing verification
        prev_code_step = steps[-1].id
        steps.append(WorkflowStep(
            id="step-testing",
            name="Execute pytest Test Validation",
            target_engine="Testing Engine",
            dependencies=[prev_code_step]
        ))

        # 5. Documentation
        steps.append(WorkflowStep(
            id="step-documentation",
            name="Compile Technical README documentation",
            target_engine="Documentation Engine",
            dependencies=["step-testing"]
        ))

        # 6. Deployment preparation
        if "deploy" in prompt or "docker" in prompt or "production" in prompt or "kubernetes" in prompt:
            steps.append(WorkflowStep(
                id="step-deployment",
                name="Generate Dockerfile and CI Pipeline Configurations",
                target_engine="Deployment Engine",
                dependencies=["step-documentation"]
            ))

        return Workflow(
            id=f"wf-{int(datetime_to_timestamp())}",
            steps=steps
        )

def datetime_to_timestamp() -> float:
    from datetime import datetime
    return datetime.utcnow().timestamp()
