"""Artifact Manager catalogs generated deployment configurations.
"""

from typing import List
from app.agents.software_engineer.deployment.interfaces import IArtifactManager
from app.agents.software_engineer.deployment.models import DeploymentArtifact

class LocalArtifactManager(IArtifactManager):
    """Stores generated deployment configs tracking checklists."""

    def __init__(self) -> None:
        self.artifacts: List[DeploymentArtifact] = []

    def track_artifact(self, artifact: DeploymentArtifact) -> None:
        """Appends generated config files details to track list."""
        self.artifacts.append(artifact)

    def list_artifacts(self) -> List[DeploymentArtifact]:
        """Lists all tracked config templates."""
        return self.artifacts
