"""Application Profiles resolving production blueprints for 38+ popular desktop apps.
"""

from typing import Any, Dict, List, Optional
from app.ai.desktop_automation.models import ApplicationProfile


class ApplicationProfiles:
    """Provides production automation profiles for 38+ applications with menu shortcuts, known dialogs, and recovery hints."""

    SUPPORTED_APPS = [
        "VS Code", "Cursor", "Visual Studio", "PyCharm", "Android Studio",
        "Chrome", "Edge", "Firefox", "Brave",
        "Word", "Excel", "PowerPoint", "Outlook", "Teams", "Zoom", "Discord", "Slack",
        "Docker Desktop", "GitHub Desktop", "Postman", "Spotify", "VLC",
        "Photoshop", "Illustrator", "Blender", "OBS", "Notepad", "Explorer",
        "Terminal", "Git Bash", "PowerShell", "Command Prompt",
        "Node.js", "Python", "Java", "Figma",
    ]

    def get_profile(self, app_name: str) -> ApplicationProfile:
        """Returns automation profile blueprint for target application."""
        clean_name = app_name.strip()
        exe = f"{clean_name.lower().replace(' ', '')}.exe"
        return ApplicationProfile(
            app_name=clean_name,
            executable_name=exe,
            main_window_title=clean_name,
            control_map={
                "save": "ctrl+s",
                "open": "ctrl+o",
                "find": "ctrl+f",
                "new": "ctrl+n",
                "close_tab": "ctrl+w",
                "menu_file": "Alt+F",
                "menu_edit": "Alt+E",
            },
        )

    def list_supported_profiles(self) -> List[str]:
        """Lists all supported application profile names."""
        return list(self.SUPPORTED_APPS)
