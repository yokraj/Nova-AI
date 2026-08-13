"""Office Plugin providing document creation, spreadsheet processing, and presentation formatting."""

from app.ai.plugins.models import PermissionType, RiskLevel
from app.ai.plugins.sdk.context import PluginContext
from app.ai.plugins.sdk.decorators import capability, nova_plugin
from app.ai.plugins.sdk.plugin import BasePlugin
from app.ai.plugins.sdk.responses import PluginResult


@nova_plugin(
    name="Office",
    version="1.0.0",
    description="Office documents, spreadsheets, and presentation plugin.",
    permissions=[PermissionType.FILE_SYSTEM],
)
class OfficePlugin(BasePlugin):
    """Reference implementation of Office Plugin."""

    @capability(
        name="create_document",
        description="Create a Word/Text document",
        voice_intents=["create document", "write word doc"],
        risk_level=RiskLevel.MEDIUM,
    )
    async def create_document(self, context: PluginContext) -> PluginResult:
        title = context.parameters.get("title", "Doc1")
        return PluginResult.ok(data={"status": "created", "document": title})

    @capability(
        name="read_spreadsheet",
        description="Read tabular data from Excel/CSV file",
        voice_intents=["read spreadsheet", "open excel"],
        risk_level=RiskLevel.LOW,
    )
    async def read_spreadsheet(self, context: PluginContext) -> PluginResult:
        return PluginResult.ok(data={"rows": 10, "columns": 5})

    @capability(
        name="format_presentation",
        description="Format PowerPoint slides layout",
        voice_intents=["format slides", "create presentation"],
        risk_level=RiskLevel.LOW,
    )
    async def format_presentation(self, context: PluginContext) -> PluginResult:
        return PluginResult.ok(data={"slides_formatted": 4})
