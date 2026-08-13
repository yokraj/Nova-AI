"""Credential Manager managing local encrypted user credentials."""

from typing import Dict, Optional
import structlog

from app.ai.services.models import CredentialRecord

logger = structlog.get_logger("credential_manager")


class CredentialManager:
    """Stores and retrieves service authentication credentials locally."""

    def __init__(self) -> None:
        self._credentials: Dict[str, CredentialRecord] = {
            "train_booking": CredentialRecord(service_id="train_booking", username="irctc_user_01", domain="irctc.co.in"),
            "passport_renewal": CredentialRecord(service_id="passport_renewal", username="passport_user_01", domain="passportindia.gov.in"),
            "fund_transfer": CredentialRecord(service_id="fund_transfer", username="bank_user_01", domain="netbanking.com"),
        }

    async def get_credential(self, service_id: str) -> Optional[CredentialRecord]:
        """Retrieve stored credential."""
        cred = self._credentials.get(service_id)
        if cred:
            logger.info("Retrieved stored credential", service_id=service_id, username=cred.username)
        return cred

    async def save_credential(self, service_id: str, username: str, domain: str = "") -> CredentialRecord:
        """Save credential record."""
        cred = CredentialRecord(service_id=service_id, username=username, domain=domain)
        self._credentials[service_id] = cred
        logger.info("Saved service credential", service_id=service_id, username=username)
        return cred
