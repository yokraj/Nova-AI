"""Email Plugin providing sending, inbox reading, and email searching."""

from app.ai.plugins.models import PermissionType, RiskLevel
from app.ai.plugins.sdk.context import PluginContext
from app.ai.plugins.sdk.decorators import capability, nova_plugin
from app.ai.plugins.sdk.plugin import BasePlugin
from app.ai.plugins.sdk.responses import PluginResult


@nova_plugin(
    name="Email",
    version="1.0.0",
    description="Email sending, reading, and inbox search plugin.",
    permissions=[PermissionType.EMAIL, PermissionType.NETWORK],
)
class EmailPlugin(BasePlugin):
    """Reference implementation of Email Plugin."""

    @capability(
        name="send_email",
        description="Send an email to a recipient",
        voice_intents=["send email", "send report", "write email"],
        risk_level=RiskLevel.HIGH,
    )
    async def send_email(self, context: PluginContext) -> PluginResult:
        to = context.parameters.get("to", "recipient@example.com")
        subject = context.parameters.get("subject", "Nova AI Report")
        return PluginResult.ok(data={"status": "sent", "to": to, "subject": subject})

    @capability(
        name="read_inbox",
        description="Retrieve unread messages from inbox",
        voice_intents=["read inbox", "check email", "unread messages"],
        risk_level=RiskLevel.MEDIUM,
    )
    async def read_inbox(self, context: PluginContext) -> PluginResult:
        return PluginResult.ok(data={"unread_count": 2, "messages": ["Meeting tomorrow", "Project status"]})

    @capability(
        name="search_emails",
        description="Search emails by sender or keyword",
        voice_intents=["search email", "find email"],
        risk_level=RiskLevel.LOW,
    )
    async def search_emails(self, context: PluginContext) -> PluginResult:
        query = context.parameters.get("query", "")
        return PluginResult.ok(data={"query": query, "results": 2})
