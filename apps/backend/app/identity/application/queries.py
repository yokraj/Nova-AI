"""Application queries for the Nova AI Identity bounded context.

Defines input parameter query structures driving profile retrieval lookups.
"""

import uuid
from pydantic import BaseModel, Field


class GetProfileQuery(BaseModel):
    """Query requesting profile details lookup for an active user ID."""

    user_id: uuid.UUID = Field(
        ..., description="The user UUID whose profile is requested."
    )


class GetUserByIdQuery(BaseModel):
    """Query requesting User registration details lookup by UUID."""

    user_id: uuid.UUID = Field(..., description="Target User UUID.")
