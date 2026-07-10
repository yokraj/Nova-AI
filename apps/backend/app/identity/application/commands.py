"""Application commands for the Nova AI Identity bounded context.

Defines input parameter command structures driving account modifications actions.
"""

from typing import Optional
import uuid
from pydantic import BaseModel, Field


class RegisterUserCommand(BaseModel):
    """Command requesting registration of a new user account profile."""

    email: str = Field(..., description="Target user email address.")
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    display_name: Optional[str] = Field(None, max_length=100)


class LoginCommand(BaseModel):
    """Command requesting token generation via credentials validation."""

    username_or_email: str = Field(
        ..., description="Unique email address or account username string."
    )
    password: str = Field(..., description="Plain-text password to verify.")


class RefreshTokenCommand(BaseModel):
    """Command requesting access token rotation using a valid refresh token."""

    refresh_token: str = Field(
        ..., description="Active unrevoked refresh token string."
    )


class LogoutCommand(BaseModel):
    """Command requesting session revocation."""

    refresh_token: str = Field(
        ..., description="The refresh token to invalidate."
    )


class UpdateProfileCommand(BaseModel):
    """Command requesting profile details modifications."""

    user_id: uuid.UUID = Field(..., description="Target User UUID.")
    display_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=255)
