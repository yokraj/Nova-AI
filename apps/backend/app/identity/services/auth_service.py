"""Authentication and Session control business services for Nova AI.

Orchestrates register, login, logout, and token family rotation workflows.
"""

from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status

from app.database.unit_of_work import UnitOfWork
from app.identity.domain.refresh_token import RefreshToken
from app.identity.domain.user import User
from app.identity.infrastructure.security import (
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    generate_refresh_token,
    hash_password,
    verify_password,
)
from app.identity.infrastructure.token_repository import RefreshTokenRepository
from app.identity.infrastructure.user_repository import UserRepository
from app.services.base import BaseService


class AuthService(BaseService):
    """Business service coordinating registration, logins, and session lifecycles."""

    def __init__(
        self,
        uow: UnitOfWork,
        user_repository: UserRepository,
        token_repository: RefreshTokenRepository,
    ) -> None:
        """Initializes the AuthService.

        Args:
            uow: Transaction Unit of Work block wrapper.
            user_repository: Concrete UserRepository instance.
            token_repository: Concrete RefreshTokenRepository instance.
        """
        super().__init__()
        self.uow = uow
        self.user_repo = user_repository
        self.token_repo = token_repository

    async def register(
        self, email: str, username: str, password: str, display_name: str | None = None
    ) -> User:
        """Registers a new user record after checking duplicate fields.

        Args:
            email: Unique user email string.
            username: Unique user identifier string.
            password: Plaintext password.
            display_name: Optional profile name details.

        Returns:
            The created User entity mapping.

        Raises:
            HTTPException: If email or username is already registered.
        """
        async with self.uow:
            if await self.user_repo.get_by_email(email):
                self.log_error("registration_failed_email_taken", email=email)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered.",
                )

            if await self.user_repo.get_by_username(username):
                self.log_error("registration_failed_username_taken", username=username)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken.",
                )

            hashed_password = hash_password(password)
            user = User(
                email=email,
                username=username,
                password_hash=hashed_password,
                display_name=display_name,
                status="active",
                role="user",
            )
            await self.user_repo.create(user)
            self.log_info(
                "user_registered", email=email, username=username
            )
            return user

    async def login(self, username_or_email: str, password: str) -> dict:
        """Authenticates user credentials and returns tokens.

        Args:
            username_or_email: Username string or email.
            password: Plaintext password.

        Returns:
            A dictionary containing access_token and refresh_token.

        Raises:
            HTTPException: If verification checks fail or the account is suspended.
        """
        async with self.uow:
            user = await self.user_repo.get_by_email(username_or_email)
            if not user:
                user = await self.user_repo.get_by_username(username_or_email)

            if not user or not verify_password(password, user.password_hash):
                self.log_error("login_failed_invalid_credentials", identity=username_or_email)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password.",
                )

            if user.status != "active":
                self.log_error("login_failed_inactive_account", user_id=str(user.id))
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is suspended.",
                )

            access_token = create_access_token(
                {"sub": str(user.id), "role": user.role}
            )
            refresh_token_val = generate_refresh_token()
            expires_at = datetime.now(timezone.utc) + timedelta(
                days=REFRESH_TOKEN_EXPIRE_DAYS
            )

            token_record = RefreshToken(
                user_id=user.id,
                token=refresh_token_val,
                expires_at=expires_at,
                revoked=False,
            )
            await self.token_repo.create(token_record)
            self.log_info("user_login_completed", user_id=str(user.id))
            return {
                "access_token": access_token,
                "refresh_token": refresh_token_val,
            }

    async def refresh_tokens(self, refresh_token_val: str) -> dict:
        """Rotates refresh tokens and issues a new access token.

        If a revoked token is reused, revokes the user's entire family.

        Args:
            refresh_token_val: The hex refresh token string.

        Returns:
            A dictionary containing new access_token and refresh_token.

        Raises:
            HTTPException: If validation checks fail or security anomalies occur.
        """
        async with self.uow:
            token_record = await self.token_repo.get_by_token(refresh_token_val)
            if not token_record:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token.",
                )

            # Stolen token family reuse detection (Security Guard)
            if token_record.revoked:
                # Force revocation of all tokens for this user session family
                await self.token_repo.revoke_user_tokens(token_record.user_id)
                self.log_error(
                    "security_alert_refresh_token_reused",
                    user_id=str(token_record.user_id),
                    reused_token=refresh_token_val,
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session expired due to security alert.",
                )

            # Ensure expires_at comparison works with timezone settings
            exp = token_record.expires_at.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Expired refresh token.",
                )

            user = await self.user_repo.get(token_record.user_id)
            if not user or user.status != "active":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive.",
                )

            # Rotate current token (revoke it)
            token_record.revoked = True

            # Generate new pair
            new_access_token = create_access_token(
                {"sub": str(user.id), "role": user.role}
            )
            new_refresh_token_val = generate_refresh_token()
            new_expires_at = datetime.now(timezone.utc) + timedelta(
                days=REFRESH_TOKEN_EXPIRE_DAYS
            )

            new_token_record = RefreshToken(
                user_id=user.id,
                token=new_refresh_token_val,
                expires_at=new_expires_at,
                revoked=False,
            )
            await self.token_repo.create(new_token_record)
            self.log_info("refresh_tokens_rotated", user_id=str(user.id))
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token_val,
            }

    async def logout(self, refresh_token_val: str) -> None:
        """Revokes a refresh token to terminate the session.

        Args:
            refresh_token_val: The refresh token to invalidate.
        """
        async with self.uow:
            token_record = await self.token_repo.get_by_token(refresh_token_val)
            if token_record:
                token_record.revoked = True
                self.log_info(
                    "session_logout_completed",
                    user_id=str(token_record.user_id),
                )
