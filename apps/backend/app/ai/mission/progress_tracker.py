"""Progress Tracker maintaining ETA metrics and voice progress indicators.
"""

from typing import Dict, Any, List
from app.ai.mission.models import ProgressReport

class ProgressTracker:
    """Tracks percentage complete and formats spoken progress reports."""

    def __init__(self, mission_id: str) -> None:
        self.mission_id = mission_id
        self.percentage = 0.0
        self.completed: List[str] = []
        self.remaining: List[str] = []
        self.stage = "planning"

    def update_progress(self, percentage: float, completed: List[str], remaining: List[str], stage: str) -> None:
        """Saves telemetry progress parameters."""
        self.percentage = percentage
        self.completed = completed
        self.remaining = remaining
        self.stage = stage

    def generate_report(self) -> ProgressReport:
        """Returns Pydantic progress report model."""
        return ProgressReport(
            mission_id=self.mission_id,
            percentage=self.percentage,
            completed_tasks=list(self.completed),
            remaining_tasks=list(self.remaining),
            current_stage=self.stage,
            eta_seconds=len(self.remaining) * 120.0
        )

    def generate_voice_summary(self) -> str:
        """Formats conversational updates spoken by voice modules."""
        if self.percentage >= 100.0:
            return "Mission completed successfully."
        if self.stage == "paused":
            return "Deployment requires your approval."
        
        pct_int = int(self.percentage)
        return f"Mission is in the {self.stage} stage, and is {pct_int}% complete."
