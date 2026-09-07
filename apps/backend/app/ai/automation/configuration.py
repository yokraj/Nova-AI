"""Configuration settings for the Native Desktop & Browser Automation Engine."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AutomationConfiguration(BaseSettings):
    """Central configuration for desktop, window, mouse, keyboard, OCR, and browser automation."""

    model_config = SettingsConfigDict(
        env_prefix="NOVA_AUTOMATION_",
        case_sensitive=False,
        extra="ignore",
    )

    enabled: bool = Field(
        default=True,
        description="Whether automation engine is active.",
    )
    permission_level: str = Field(
        default="STANDARD",
        description="Automation permission level ('STANDARD', 'STRICT', 'ADMIN').",
    )
    provider: str = Field(
        default="pyautogui",
        description="Automation provider driver ('pyautogui', 'win32', 'mock').",
    )

    default_browser: str = Field(
        default="chrome",
        description="Default web browser driver ('chrome', 'edge', 'firefox').",
    )

    headless_browser: bool = Field(
        default=False,
        description="Whether to launch browser in headless mode.",
    )
    screen_width: int = Field(
        default=1920,
        description="Primary display screen width in pixels.",
    )
    screen_height: int = Field(
        default=1080,
        description="Primary display screen height in pixels.",
    )
    ocr_enabled: bool = Field(
        default=True,
        description="Whether OCR text extraction from screens/dialogs is enabled.",
    )
    mouse_speed_seconds: float = Field(
        default=0.2,
        description="Default duration for smooth mouse cursor movements.",
    )
    safety_dry_run: bool = Field(
        default=False,
        description="Simulate dangerous actions without firing real input events when set.",
    )
    downloads_dir: str = Field(
        default="./data/downloads",
        description="Default local directory for intercepted file downloads.",
    )

    @property
    def safety(self) -> "AutomationConfiguration":
        return self

    @property
    def dry_run(self) -> bool:
        return self.safety_dry_run


SafetyConfiguration = AutomationConfiguration


