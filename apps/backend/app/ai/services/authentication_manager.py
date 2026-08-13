"""Authentication Manager handling site login flows, credentials, and session restoration."""

import structlog

from app.ai.services.credential_manager import CredentialManager
from app.ai.services.exceptions import AuthenticationFailedError
from app.ai.services.session_manager import SessionManager

logger = structlog.get_logger("authentication_manager")


class AuthenticationManager:
    """Handles site login flows and session restores."""

    def __init__(self) -> None:
        self.credentials = CredentialManager()
        self.sessions = SessionManager()

    async def ensure_authenticated(self, service_id: str) -> bool:
        """Verify or establish authenticated session for service portal."""
        if await self.sessions.is_authenticated(service_id):
            return True

        cred = await self.credentials.get_credential(service_id)
        if not cred:
            logger.info("No saved credential found, continuing as guest or prompting login", service_id=service_id)
            return False

        logger.info("Authenticating service portal with stored credentials", service_id=service_id, user=cred.username)
        await self.sessions.mark_authenticated(service_id, True)
        return True
