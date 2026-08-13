"""Contact Manager managing personal address book contacts."""

from typing import List
import structlog

from app.ai.assistant.models import ContactRecord

logger = structlog.get_logger("contact_manager")


class ContactManager:
    """Manages address book contacts, emails, and phone numbers."""

    def __init__(self) -> None:
        self._contacts: List[ContactRecord] = [
            ContactRecord(name="Alice Smith", email="alice@nova.ai", relationship="colleague"),
            ContactRecord(name="Bob Jones", email="bob@nova.ai", relationship="manager"),
        ]

    async def list_contacts(self) -> List[ContactRecord]:
        """List contacts."""
        return list(self._contacts)
