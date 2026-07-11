"""SoftwareEngineerContext modeling session parameters.
"""

from typing import List, Optional
import uuid
from pydantic import BaseModel, Field


class SoftwareEngineerContext(BaseModel):
    """Active execution context for the Software Engineering Agent."""

    workspace: str = Field("", description="Active workspace path.")
    repository: str = Field("", description="Active repository name.")
    current_branch: str = Field("main", description="Active git branch.")
    language: str = Field("python", description="Active programming language.")
    framework: str = Field("", description="Active framework framework (e.g. 'fastapi').")
    user_request: str = Field("", description="The original user request prompt.")
    conversation_id: Optional[uuid.UUID] = None
    execution_id: Optional[uuid.UUID] = None
    opened_files: List[str] = Field(default_factory=list, description="List of currently opened files.")
    active_file: str = Field("", description="Active focus file path.")
