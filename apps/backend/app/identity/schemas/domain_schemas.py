"""Validation schemas mappings for Identity HTTP requests and responses.

Defines serialized fields constraints for HTTP registration, login, and profile.
"""

from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """Payload to register a new user account."""

    email: str = Field(..., description="Target email address.")
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    display_name: Optional[str] = Field(None, max_length=100)


class RegisterResponse(BaseModel):
    """Payload returned upon successful registration."""

    id: uuid.UUID
    email: str
    username: str
    display_name: Optional[str]
    role: str
    status: str
    created_at: datetime


class LoginRequest(BaseModel):
    """Payload to authenticate credentials."""

    username_or_email: str = Field(..., description="Username or email.")
    password: str = Field(..., description="Verification password.")


class LoginResponse(BaseModel):
    """Payload returned upon successful authentication containing access tokens."""

    access_token: str = Field(..., description="Access token JWT.")
    refresh_token: str = Field(..., description="Rotatable refresh token value.")
    token_type: str = Field("bearer", description="Token schema type.")


class ProfileResponse(BaseModel):
    """Payload returned when fetching user profile details."""

    id: uuid.UUID
    email: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    role: str
    status: str
    created_at: datetime
    updated_at: datetime


class UpdateProfileRequest(BaseModel):
    """Payload to update optional profile fields."""

    display_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=255)
