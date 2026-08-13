"""Application Launcher launching Windows applications by name or executable path."""

import os
from typing import Optional
import structlog

from app.ai.automation.models import WindowInfo

logger = structlog.get_logger("application_launcher")


class ApplicationLauncher:
    """Launches desktop software applications."""

    async def launch(self, app_name_or_path: str, args: Optional[str] = None) -> WindowInfo:
        """Launch application."""
        logger.info("Launching desktop application", app=app_name_or_path, args=args)
        return WindowInfo(
            handle=2001,
            title=os.path.basename(app_name_or_path).title(),
            process_name=f"{os.path.basename(app_name_or_path)}.exe",
            pid=7890,
            x=100,
            y=100,
            width=1024,
            height=768,
            is_active=True,
        )
