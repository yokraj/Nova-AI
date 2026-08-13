"""Consent Manager tracking explicit user session consents.
"""

from typing import Dict

class ConsentManager:
    """Manages active session-scoped consent mappings."""

    def __init__(self) -> None:
        # Action string -> Granted bool
        self._consents: Dict[str, bool] = {}

    def give_consent(self, action: str) -> None:
        """Gives user consent to execute target action."""
        self._consents[action] = True

    def revoke_consent(self, action: str) -> None:
        """Revokes user consent."""
        self._consents[action] = False

    def has_consent(self, action: str) -> bool:
        """Returns True if user has consented to this action."""
        return self._consents.get(action, False)
