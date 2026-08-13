"""Docker Generator implements IContainerGenerator, managing container file creations.
"""

from app.agents.software_engineer.deployment.interfaces import IContainerGenerator
from app.agents.software_engineer.deployment.models import EnvironmentInfo, DockerConfiguration
from app.agents.software_engineer.deployment.dockerfile_generator import DockerfileGenerator
from app.agents.software_engineer.deployment.compose_generator import DockerComposeGenerator

class LocalContainerGenerator(IContainerGenerator):
    """Combines Dockerfile and compose configurations into a unified DockerConfiguration."""

    def __init__(self) -> None:
        self.dockerfile_gen = DockerfileGenerator()
        self.compose_gen = DockerComposeGenerator()

    def generate(self, project_path: str, env_info: EnvironmentInfo) -> DockerConfiguration:
        """Runs generators to build deployment configuration payloads."""
        dockerfile_content = self.dockerfile_gen.generate_dockerfile(
            env_info.framework or "generic", env_info.runtime_version or "latest"
        )
        compose_content = self.compose_gen.generate_compose(
            env_info.framework or "generic", env_info.database, env_info.required_services
        )

        base_image = "python:3.12-slim"
        if env_info.language == "Node.js":
            base_image = "node:20-alpine"
        elif env_info.language == "Java":
            base_image = "eclipse-temurin:17-jre-jammy"

        port = 8000
        if (env_info.framework or "").lower() == "spring boot":
            port = 8080
        elif (env_info.framework or "").lower() == "react":
            port = 80

        return DockerConfiguration(
            dockerfile_content=dockerfile_content,
            compose_content=compose_content,
            base_image=base_image,
            ports=[port],
        )
