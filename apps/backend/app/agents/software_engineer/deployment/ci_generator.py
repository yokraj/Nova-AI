"""CI Generator integrates GHA, GitLab CI, and Jenkinsfile pipelines.
"""

import os
from app.agents.software_engineer.deployment.interfaces import IPipelineGenerator
from app.agents.software_engineer.deployment.models import EnvironmentInfo, PipelineConfiguration
from app.agents.software_engineer.deployment.github_actions_generator import GitHubActionsGenerator
from app.agents.software_engineer.deployment.pipeline_generator import PipelineGenerator as OtherPipelineGenerator

class CIGenerator(IPipelineGenerator):
    """Generates all pipeline configurations and consolidates them."""

    def __init__(self) -> None:
        self.gha_gen = GitHubActionsGenerator()
        self.other_gen = OtherPipelineGenerator()

    def generate(self, project_path: str, env_info: EnvironmentInfo) -> PipelineConfiguration:
        """Drafts all target pipelines for the project environment."""
        project_name = os.path.basename(project_path) or "app"
        gha_content = self.gha_gen.generate_pipeline(
            project_name, env_info.language, env_info.package_manager or "pip"
        )
        gitlab_content = self.other_gen.generate_gitlab_ci(project_name, env_info.language)
        jenkins_content = self.other_gen.generate_jenkinsfile(project_name)

        return PipelineConfiguration(
            github_actions_yaml=gha_content,
            gitlab_ci_yaml=gitlab_content,
            jenkinsfile_content=jenkins_content,
        )
