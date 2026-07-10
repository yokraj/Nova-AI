"""Application use cases (CQRS handlers) for the Nova AI Identity bounded context.

Implements pure business workflows for account registrations, credential logins,
refresh token rotations, logouts, and user profile queries/modifications.
"""

from datetime import UTC, datetime, timedelta
import uuid

from app.database.models import Session, User
from app.database.unit_of_work import UnitOfWork
from app.identity.application.commands import (
    LoginCommand,
    LogoutCommand,
    RefreshTokenCommand,
    RegisterUserCommand,
    UpdateProfileCommand,
)
from app.identity.application.queries import GetProfileQuery
from app.identity.repositories.interfaces import (
    IRefreshTokenRepository,
    ISessionRepository,
    IUserRepository,
)
from app.identity.schemas.domain_schemas import (
    LoginResponse,
    ProfileResponse,
    RegisterResponse,
)
from app.identity.services.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.identity.services.password_hasher import PasswordHasher
from app.identity.services.security_facade import SecurityService


class RegisterUserUseCase:
    """Business workflow handling registration of a new user account."""

    def __init__(
        self,
        uow: UnitOfWork,
        user_repo: IUserRepository,
        hasher: PasswordHasher,
    ) -> None:
        """Initializes the RegisterUserUseCase.

        Args:
            uow: Asynchronous UnitOfWork coordinator.
            user_repo: User repository contract.
            hasher: Password hasher service.
        """
        self.uow = uow
        self.user_repo = user_repo
        self.hasher = hasher

    async def execute(self, command: RegisterUserCommand) -> RegisterResponse:
        """Executes account registration checking email and username uniqueness.

        Args:
            command: RegisterUserCommand parameters.

        Returns:
            DTO containing the created user profile metadata.

        Raises:
            InvalidCredentialsError: If email or username is already registered.
        """
        if await self.user_repo.get_by_email(command.email):
            raise InvalidCredentialsError("Email address is already registered.")
        if await self.user_repo.get_by_username(command.username):
            raise InvalidCredentialsError("Username is already registered.")

        # Hash credential
        pwd_hash = self.hasher.hash(command.password)

        user = User(
            id=uuid.uuid4(),
            email=command.email,
            username=command.username,
            password_hash=pwd_hash,
            display_name=command.display_name,
            role="user",
            status="active",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        async with self.uow:
            await self.user_repo.save(user)

        return RegisterResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            display_name=user.display_name,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
        )


class LoginUseCase:
    """Business workflow handling credentials login and session generation."""

    def __init__(
        self,
        uow: UnitOfWork,
        user_repo: IUserRepository,
        security: SecurityService,
        session_repo: ISessionRepository,
    ) -> None:
        """Initializes the LoginUseCase.

        Args:
            uow: Asynchronous UnitOfWork coordinator.
            user_repo: User repository contract.
            security: Consolidated SecurityService facade.
            session_repo: Session repository contract.
        """
        self.uow = uow
        self.user_repo = user_repo
        self.security = security
        self.session_repo = session_repo

    async def execute(self, command: LoginCommand) -> LoginResponse:
        """Validates credentials and generates access/refresh tokens.

        Args:
            command: LoginCommand parameters.

        Returns:
            DTO containing generated token elements.

        Raises:
            InvalidCredentialsError: If credentials or account status checks fail.
        """
        user = await self.user_repo.get_by_email(command.username_or_email)
        if not user:
            user = await self.user_repo.get_by_username(
                command.username_or_email
            )

        if not user or not self.security.verify_password(
            command.password, user.password_hash
        ):
            raise InvalidCredentialsError("Invalid credentials provided.")

        if user.status != "active":
            raise InvalidCredentialsError(
                "User account is suspended or inactive."
            )

        async with self.uow:
            # Generate tokens
            access_token = self.security.generate_access_token(
                str(user.id), {"email": user.email, "role": user.role}
            )
            refresh_record = await self.security.create_refresh_token_record(
                user.id
            )

            # Persist session validation token
            session_val = self.security.generate_secure_token()
            expires = datetime.now(UTC) + timedelta(
                minutes=self.security.jwt.access_token_expire_minutes
            )
            session_record = Session(
                user_id=user.id,
                token=session_val,
                expires_at=expires,
            )
            await self.session_repo.save(session_record)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_record.token,
            token_type="bearer",
        )


class RefreshTokenUseCase:
    """Business workflow handling refresh token family rotations."""

    def __init__(
        self,
        uow: UnitOfWork,
        user_repo: IUserRepository,
        security: SecurityService,
    ) -> None:
        """Initializes the RefreshTokenUseCase.

        Args:
            uow: Asynchronous UnitOfWork coordinator.
            user_repo: User repository contract.
            security: Consolidated SecurityService facade.
        """
        self.uow = uow
        self.user_repo = user_repo
        self.security = security

    async def execute(self, command: RefreshTokenCommand) -> LoginResponse:
        """Verifies old token and issues rotated tokens family.

        Args:
            command: RefreshTokenCommand parameters.

        Returns:
            DTO containing rotated access/refresh tokens.

        Raises:
            InvalidTokenError: If associated user account cannot be found.
        """
        async with self.uow:
            # Rotate refresh token
            new_record = await self.security.rotate_refresh_token(
                command.refresh_token
            )
            user = await self.user_repo.get_by_id(new_record.user_id)
            if not user:
                raise InvalidTokenError("User associated with token not found.")

            access_token = self.security.generate_access_token(
                str(user.id), {"email": user.email, "role": user.role}
            )

        return LoginResponse(
            access_token=access_token,
            refresh_token=new_record.token,
            token_type="bearer",
        )


class LogoutUseCase:
    """Business workflow terminating active refresh tokens and sessions."""

    def __init__(
        self,
        uow: UnitOfWork,
        token_repo: IRefreshTokenRepository,
    ) -> None:
        """Initializes the LogoutUseCase.

        Args:
            uow: Asynchronous UnitOfWork coordinator.
            token_repo: RefreshToken repository contract.
        """
        self.uow = uow
        self.token_repo = token_repo

    async def execute(self, command: LogoutCommand) -> None:
        """Revokes token records in database.

        Args:
            command: LogoutCommand parameters.

        Raises:
            InvalidTokenError: If token does not exist.
        """
        record = await self.token_repo.get_by_token(command.refresh_token)
        if not record:
            raise InvalidTokenError("Refresh token not found.")

        async with self.uow:
            record.is_revoked = True
            await self.token_repo.save(record)


class GetProfileUseCase:
    """Business workflow retrieving profile details responses."""

    def __init__(self, user_repo: IUserRepository) -> None:
        """Initializes the GetProfileUseCase.

        Args:
            user_repo: User repository contract.
        """
        self.user_repo = user_repo

    async def execute(self, query: GetProfileQuery) -> ProfileResponse:
        """Queries user profile details DTO.

        Args:
            query: GetProfileQuery parameters.

        Returns:
            ProfileResponse DTO containing user info.

        Raises:
            InvalidCredentialsError: If user ID does not exist.
        """
        user = await self.user_repo.get_by_id(query.user_id)
        if not user:
            raise InvalidCredentialsError("User account not found.")

        return ProfileResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class UpdateProfileUseCase:
    """Business workflow modifying user display name or avatar details."""

    def __init__(self, uow: UnitOfWork, user_repo: IUserRepository) -> None:
        """Initializes the UpdateProfileUseCase.

        Args:
            uow: Asynchronous UnitOfWork coordinator.
            user_repo: User repository contract.
        """
        self.uow = uow
        self.user_repo = user_repo

    async def execute(self, command: UpdateProfileCommand) -> ProfileResponse:
        """Updates profile columns inside UoW.

        Args:
            command: UpdateProfileCommand parameters.

        Returns:
            ProfileResponse DTO containing updated user details.

        Raises:
            InvalidCredentialsError: If user ID does not exist.
        """
        user = await self.user_repo.get_by_id(command.user_id)
        if not user:
            raise InvalidCredentialsError("User account not found.")

        async with self.uow:
            if command.display_name is not None:
                user.display_name = command.display_name
            if command.avatar_url is not None:
                user.avatar_url = command.avatar_url
            await self.user_repo.save(user)

        return ProfileResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
