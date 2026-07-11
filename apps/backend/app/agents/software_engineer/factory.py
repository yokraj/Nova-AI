"""SoftwareEngineerFactory building default and custom agents.
"""

from typing import Any, Dict, Optional

from app.agents.software_engineer.agent import SoftwareEngineerAgent
from app.agents.software_engineer.configuration import SoftwareEngineerConfiguration
from app.agents.software_engineer.metadata import SoftwareEngineerMetadata


class SoftwareEngineerFactory:
    """Constructs configured, default, and testing Software Engineering Agent instances."""

    @staticmethod
    def create_default() -> SoftwareEngineerAgent:
        """Creates a SoftwareEngineerAgent with default parameters.

        Returns:
            Instantiated SoftwareEngineerAgent.
        """
        meta = SoftwareEngineerMetadata(
            agent_name="SoftwareEngineerAgent",
            sdk_version="1.0.0",
            runtime_version="Python 3.14",
            description="Default software engineering agent.",
        )
        config = SoftwareEngineerConfiguration()
        return SoftwareEngineerAgent(meta, config)

    @staticmethod
    def create_configured(config_dict: Dict[str, Any]) -> SoftwareEngineerAgent:
        """Creates a SoftwareEngineerAgent with custom configurations dict.

        Args:
            config_dict: Dictionary of configuration parameters.

        Returns:
            Instantiated SoftwareEngineerAgent.
        """
        meta = SoftwareEngineerMetadata(
            agent_name="SoftwareEngineerAgent", sdk_version="1.0.0", runtime_version="Python 3.14"
        )
        config = SoftwareEngineerConfiguration(**config_dict)
        return SoftwareEngineerAgent(meta, config)

    @staticmethod
    def create_testing(workspace_root: str) -> SoftwareEngineerAgent:
        """Creates a SoftwareEngineerAgent with specific testing workspace roots.

        Args:
            workspace_root: Workspace root directory path.

        Returns:
            Instantiated SoftwareEngineerAgent.
        """
        meta = SoftwareEngineerMetadata(
            agent_name="TestingSoftwareEngineerAgent",
            sdk_version="1.0.0",
            runtime_version="Python 3.14",
            description="Testing agent configuration.",
        )
        config = SoftwareEngineerConfiguration(workspace_root=workspace_root)
        return SoftwareEngineerAgent(meta, config)
