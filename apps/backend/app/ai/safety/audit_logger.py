"""Audit Logger persisting validation outcomes.
"""

from typing import List
from app.ai.safety.models import AuditRecord

class AuditLogger:
    """Logs security reviews and confirmation outcomes."""

    def __init__(self) -> None:
        self.logs: List[AuditRecord] = []

    def log_eval(self, record: AuditRecord) -> None:
        """Appends audit event to memory log lists."""
        self.logs.append(record.model_copy())

    def get_logs(self) -> List[AuditRecord]:
        """Lists logged audit trail records."""
        return list(self.logs)
