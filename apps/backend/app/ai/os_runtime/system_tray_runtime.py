"""Windows System Tray Application Runtime Daemon.
"""

from app.ai.os_runtime.interfaces import ISystemTrayRuntime
from app.ai.os_runtime.models import SystemTrayStatus


class SystemTrayRuntime(ISystemTrayRuntime):
    """Windows System Tray daemon controlling mic status, active models, quick mute, logs, diagnostics, and service exit."""

    def __init__(self) -> None:
        self.microphone_muted: bool = False
        self.listening_active: bool = True

    def get_tray_status(self) -> SystemTrayStatus:
        """Returns snapshot of current system tray status."""
        return SystemTrayStatus(
            icon_state="active" if self.listening_active and not self.microphone_muted else "muted",
            microphone_muted=self.microphone_muted,
            listening_active=self.listening_active,
            active_models_count=3,
            active_mission_name="Autonomous Refactoring Mission",
        )

    def toggle_mute(self) -> bool:
        """Toggles microphone mute state."""
        self.microphone_muted = not self.microphone_muted
        return self.microphone_muted
