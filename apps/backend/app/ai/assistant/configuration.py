"""Configuration settings for the Autonomous Personal Assistant & Life Management Engine."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AssistantConfiguration(BaseSettings):
    """Central configuration for assistant planning, memory, proactive alerts, and routines."""

    model_config = SettingsConfigDict(
        env_prefix="NOVA_ASSISTANT_",
        case_sensitive=False,
        extra="ignore",
    )

    enabled: bool = Field(
        default=True,
        description="Whether personal assistant engine is active.",
    )
    proactive_notifications: bool = Field(
        default=True,
        description="Whether proactive reminders and break alerts are enabled.",
    )
    morning_briefing_time: str = Field(
        default="08:00",
        description="Default morning briefing time (HH:MM).",
    )
    evening_summary_time: str = Field(
        default="20:00",
        description="Default evening summary time (HH:MM).",
    )
    work_start_hour: int = Field(
        default=9,
        description="Default work start hour (24h).",
    )
    work_end_hour: int = Field(
        default=18,
        description="Default work end hour (24h).",
    )
    hydration_reminder_interval_hours: int = Field(
        default=2,
        description="Interval for hydration reminders.",
    )
    meeting_prep_lead_time_minutes: int = Field(
        default=15,
        description="Lead time for meeting preparation auto-missions.",
    )
