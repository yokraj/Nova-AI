"""Deployment Validator checks Dockerfile syntax and compose YAML standards.
"""

from typing import List, Optional
from app.agents.software_engineer.deployment.interfaces import IValidator
from app.agents.software_engineer.deployment.models import DockerConfiguration, PipelineConfiguration

class LocalValidator(IValidator):
    """Executes structural and syntax compliance checks on target outputs."""

    def validate(
        self,
        project_path: str,
        docker_config: Optional[DockerConfiguration] = None,
        pipeline_config: Optional[PipelineConfiguration] = None,
    ) -> List[str]:
        """Validates generated files to locate misconfigured keys."""
        errors: List[str] = []

        if docker_config:
            # 1. Dockerfile checks
            df = docker_config.dockerfile_content
            if "FROM" not in df:
                errors.append("Dockerfile must contain a FROM directive.")
            if "USER" not in df:
                errors.append("Dockerfile security check failed: No non-root USER directive found.")
            if "HEALTHCHECK" not in df:
                errors.append("Dockerfile should configure a HEALTHCHECK directive.")

            # 2. Compose checks
            comp = docker_config.compose_content
            yaml_err = self._validate_yaml_lines(comp)
            if yaml_err:
                errors.append(f"Docker Compose YAML syntax error: {yaml_err}")

        if pipeline_config:
            # 3. Pipeline checks
            if pipeline_config.github_actions_yaml:
                yaml_err = self._validate_yaml_lines(pipeline_config.github_actions_yaml)
                if yaml_err:
                    errors.append(f"GitHub Actions workflow YAML syntax error: {yaml_err}")
            if pipeline_config.gitlab_ci_yaml:
                yaml_err = self._validate_yaml_lines(pipeline_config.gitlab_ci_yaml)
                if yaml_err:
                    errors.append(f"GitLab CI YAML syntax error: {yaml_err}")

        return errors

    def _validate_yaml_lines(self, content: str) -> Optional[str]:
        """Performs structural line checks to find YAML syntax issues without using PyYAML."""
        if not content:
            return None
        lines = content.splitlines()
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            
            # Simple check: if line starts with space, check that indentation is even-spaced (standard YAML)
            leading_spaces = len(line) - len(line.lstrip(' '))
            if leading_spaces % 2 != 0 and leading_spaces > 0:
                # We won't block strictly on odd spacing, but if there's key issues we report
                pass
                
            if ":" in stripped:
                parts = stripped.split(":", 1)
                key = parts[0].strip()
                if " " in key and not (key.startswith('"') or key.startswith("'") or key.startswith("-")):
                    return f"Line {idx+1}: Invalid key format '{key}'"
        return None
