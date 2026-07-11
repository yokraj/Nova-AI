"""SDKMetadata schema describing SDK agent identity attributes.
"""

from pydantic import BaseModel, Field


class SDKMetadata(BaseModel):
    """Metadata tracking versions and identities for Agent SDK instances."""

    sdk_version: str = Field("1.0.0", description="Version identifier of the Agent SDK.")
    agent_name: str = Field(..., description="Target name of the agent inheriting this SDK.")
    runtime_version: str = Field("Python 3.14", description="Underlying runtime/python version.")
