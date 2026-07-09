"""Pydantic schemas and serialization models for Nova AI Identity bounded context.

Defines client requests and response data contracts.
"""

from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class UserRegisterRequest(BaseModel):
    """Payload schema required for user registration."""

    email: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="Must be a valid email address.",
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username containing between 3 and 50 characters.",
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Secure plaintext password of at least 8 characters.",
    )
    display_name: Optional[str] = Field(
        None, max_length=100, description="Optional profile display name."
    )


class UserLoginRequest(BaseModel):
    """Payload schema required for user login."""

    username_or_email: str = Field(
        ..., description="Username or email address identifying the user."
    )
    password: str = Field(..., description="Plaintext password to check.")


class TokenResponse(BaseModel):
    """API response model containing session authentication tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    """Payload schema required to refresh an access token."""

    refresh_token: str = Field(
        ..., description="The hexadecimal refresh token string."
    )


class UserProfileResponse(BaseModel):
    """API response model exposing user profile information details."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    status: str
    role: str
    created_at: datetime
