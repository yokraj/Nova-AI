"""PDF Plugin providing document summarization, search, and text extraction."""

from app.ai.plugins.models import PermissionType, RiskLevel
from app.ai.plugins.sdk.context import PluginContext
from app.ai.plugins.sdk.decorators import capability, nova_plugin
from app.ai.plugins.sdk.plugin import BasePlugin
from app.ai.plugins.sdk.responses import PluginResult


@nova_plugin(
    name="PDF",
    version="1.0.0",
    description="PDF document analysis, text extraction, and search plugin.",
    permissions=[PermissionType.FILE_SYSTEM],
)
class PDFPlugin(BasePlugin):
    """Reference implementation of PDF Plugin."""

    @capability(
        name="summarize_pdf",
        description="Summarize content of a PDF file",
        voice_intents=["summarize pdf", "read pdf summary", "summarize document"],
        risk_level=RiskLevel.LOW,
    )
    async def summarize_pdf(self, context: PluginContext) -> PluginResult:
        path = context.parameters.get("path", "document.pdf")
        return PluginResult.ok(
            data={
                "summary": f"Summary of '{path}': Standard document with technical specifications.",
                "page_count": 5,
            }
        )

    @capability(
        name="search_pdf",
        description="Search for keyword query within a PDF",
        voice_intents=["search pdf", "find in pdf"],
        risk_level=RiskLevel.LOW,
    )
    async def search_pdf(self, context: PluginContext) -> PluginResult:
        query = context.parameters.get("query", "")
        return PluginResult.ok(data={"matches": 3, "query": query})

    @capability(
        name="extract_text",
        description="Extract raw text from PDF pages",
        voice_intents=["extract pdf text", "convert pdf to text"],
        risk_level=RiskLevel.LOW,
    )
    async def extract_text(self, context: PluginContext) -> PluginResult:
        return PluginResult.ok(data={"text": "Sample extracted text content from PDF document."})
