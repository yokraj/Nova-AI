"""Local Bug Database caching resolutions and fixes matched by trace names offline.
"""

import json
import os
from typing import Dict, Optional

from app.agents.software_engineer.debugging.interfaces import BugDatabase
from app.agents.software_engineer.debugging.models import RepairPlan


class LocalBugDatabase(BugDatabase):
    """Saves diagnosed resolution patterns locally."""

    def __init__(self, db_file_path: str) -> None:
        self.db_file_path = os.path.abspath(db_file_path)
        self.data: Dict[str, dict] = {}
        self.load()

    def load(self) -> None:
        if os.path.exists(self.db_file_path):
            try:
                with open(self.db_file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.db_file_path), exist_ok=True)
        try:
            with open(self.db_file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def _get_key(self, exception_type: str, message: str) -> str:
        return f"{exception_type}:{message[:100]}"

    def get_known_fix(self, exception_type: str, message: str) -> Optional[RepairPlan]:
        key = self._get_key(exception_type, message)
        entry = self.data.get(key)
        if entry:
            try:
                return RepairPlan.model_validate(entry)
            except Exception:
                return None
        return None

    def record_resolution(self, exception_type: str, message: str, plan: RepairPlan) -> None:
        key = self._get_key(exception_type, message)
        self.data[key] = plan.model_dump()
        self.save()
