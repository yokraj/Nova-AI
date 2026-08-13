"""Calendar Plugin providing event creation, scheduling, and availability checks."""

from app.ai.plugins.models import PermissionType, RiskLevel
from app.ai.plugins.sdk.context import PluginContext
from app.ai.plugins.sdk.decorators import capability, nova_plugin
from app.ai.plugins.sdk.plugin import BasePlugin
from app.ai.plugins.sdk.responses import PluginResult


@nova_plugin(
    name="Calendar",
    version="1.0.0",
    description="Calendar scheduling and event management plugin.",
    permissions=[PermissionType.CALENDAR],
)
class CalendarPlugin(BasePlugin):
    """Reference implementation of Calendar Plugin."""

    @capability(
        name="create_event",
        description="Schedule a new calendar event",
        voice_intents=["create event", "schedule meeting", "add reminder"],
        risk_level=RiskLevel.MEDIUM,
    )
    async def create_event(self, context: PluginContext) -> PluginResult:
        title = context.parameters.get("title", "Meeting")
        time_str = context.parameters.get("time", "10:00 AM")
        return PluginResult.ok(data={"status": "created", "title": title, "time": time_str})

    @capability(
        name="list_events",
        description="List scheduled events for today or date",
        voice_intents=["list events", "what is on my calendar", "today schedule"],
        risk_level=RiskLevel.LOW,
    )
    async def list_events(self, context: PluginContext) -> PluginResult:
        return PluginResult.ok(data={"events": ["10:00 AM Team Sync", "02:00 PM Architecture Review"]})

    @capability(
        name="check_availability",
        description="Check if a time slot is available",
        voice_intents=["check availability", "am i free at"],
        risk_level=RiskLevel.LOW,
    )
    async def check_availability(self, context: PluginContext) -> PluginResult:
        return PluginResult.ok(data={"available": True})
