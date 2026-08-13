"""Application Profile Engine storing reusable profiles for 19 major desktop & web applications.
"""

from typing import Any, Dict, List
from app.ai.computer_vision.interfaces import IApplicationProfileEngine
from app.ai.computer_vision.models import ApplicationProfile


class ApplicationProfileEngine(IApplicationProfileEngine):
    """Application Profile Engine managing reusable UI layout blueprints."""

    def __init__(self) -> None:
        self._profiles: Dict[str, ApplicationProfile] = self._seed_profiles()

    def _seed_profiles(self) -> Dict[str, ApplicationProfile]:
        profiles: List[ApplicationProfile] = [
            ApplicationProfile(
                app_name="Windows Explorer",
                process_names=["explorer.exe"],
                common_ui_regions={"ribbon": "top", "navigation_pane": "left", "file_view": "center", "address_bar": "top_center"},
                known_menus=["File", "Home", "Share", "View"],
                expected_workflows=["navigate_folder", "copy_file", "delete_file", "search"],
                known_dialogs=["File Replace Confirmation", "Delete File Dialog", "Properties Dialog"],
            ),
            ApplicationProfile(
                app_name="Chrome",
                process_names=["chrome.exe"],
                common_ui_regions={"tab_bar": "top", "address_bar": "top_center", "web_viewport": "center", "extensions_bar": "top_right"},
                known_menus=["File", "Edit", "View", "History", "Bookmarks", "Profiles", "Tab"],
                expected_workflows=["navigate_url", "fill_form", "submit", "open_tab"],
                known_dialogs=["Save As Dialog", "Print Dialog", "Allow Permissions Popup"],
            ),
            ApplicationProfile(
                app_name="VS Code",
                process_names=["code.exe"],
                common_ui_regions={"activity_bar": "left", "sidebar": "left_center", "editor_group": "center", "terminal_panel": "bottom"},
                known_menus=["File", "Edit", "Selection", "View", "Go", "Run", "Terminal", "Help"],
                expected_workflows=["open_file", "edit_code", "run_terminal_command", "git_commit"],
                known_dialogs=["Save Changes Dialog", "Select Workspace Dialog", "Command Palette"],
            ),
            ApplicationProfile(
                app_name="Excel",
                process_names=["excel.exe"],
                common_ui_regions={"ribbon": "top", "formula_bar": "top_center", "spreadsheet_grid": "center", "sheet_tabs": "bottom_left"},
                known_menus=["File", "Home", "Insert", "Page Layout", "Formulas", "Data", "Review", "View"],
                expected_workflows=["enter_data", "apply_formula", "export_pdf", "create_chart"],
                known_dialogs=["Save As Dialog", "Format Cells Dialog", "Formula Error Alert"],
            ),
            ApplicationProfile(
                app_name="Photoshop",
                process_names=["photoshop.exe"],
                common_ui_regions={"tools_panel": "left", "canvas": "center", "layers_panel": "right", "options_bar": "top"},
                known_menus=["File", "Edit", "Image", "Layer", "Type", "Select", "Filter", "3D", "View", "Window"],
                expected_workflows=["open_image", "crop", "adjust_color", "export_png"],
                known_dialogs=["Export As Dialog", "Color Picker", "Unsaved Changes Dialog"],
            ),
            ApplicationProfile(
                app_name="Terminal",
                process_names=["cmd.exe", "powershell.exe", "wt.exe", "bash.exe"],
                common_ui_regions={"console_output": "center", "command_line_prompt": "bottom"},
                known_menus=["File", "Edit", "View", "Settings"],
                expected_workflows=["run_command", "view_output", "clear"],
                known_dialogs=["Confirm Exit"],
            ),
        ]

        # General fallbacks for remaining apps
        for app in [
            "Edge", "Firefox", "Visual Studio", "Cursor", "Antigravity", "PyCharm",
            "Android Studio", "Word", "PowerPoint", "Outlook", "Teams", "Blender", "Settings"
        ]:
            profiles.append(
                ApplicationProfile(
                    app_name=app,
                    process_names=[f"{app.lower().replace(' ', '')}.exe"],
                    common_ui_regions={"main_window": "center", "menu_bar": "top"},
                    known_menus=["File", "Edit", "View", "Help"],
                    expected_workflows=["open", "edit", "save"],
                    known_dialogs=["Confirm Dialog", "Settings Dialog"],
                )
            )

        return {p.app_name.lower(): p for p in profiles}

    async def get_profile(self, app_name_or_process: str) -> ApplicationProfile:
        """Retrieves profile matching application name or process.

        Args:
            app_name_or_process: App name or process executable.

        Returns:
            ApplicationProfile model.
        """
        key = app_name_or_process.lower()
        if key in self._profiles:
            return self._profiles[key]

        for p in self._profiles.values():
            if any(proc.lower() in key for proc in p.process_names):
                return p

        return ApplicationProfile(
            app_name=app_name_or_process,
            process_names=[app_name_or_process],
            common_ui_regions={"main_viewport": "center"},
            known_menus=["File", "Edit", "Help"],
            expected_workflows=["interact"],
            known_dialogs=["Dialog"],
        )
