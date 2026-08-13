"""File Plugin providing local file reading, writing, directory listing, and file info."""

import os
from app.ai.plugins.models import PermissionType, RiskLevel
from app.ai.plugins.sdk.context import PluginContext
from app.ai.plugins.sdk.decorators import capability, nova_plugin
from app.ai.plugins.sdk.plugin import BasePlugin
from app.ai.plugins.sdk.responses import PluginResult


@nova_plugin(
    name="File",
    version="1.0.0",
    description="Local filesystem interaction plugin.",
    permissions=[PermissionType.FILE_SYSTEM],
)
class FilePlugin(BasePlugin):
    """Reference implementation of File Plugin."""

    @capability(
        name="read_file",
        description="Read text contents of a file",
        voice_intents=["read file", "show file content"],
        risk_level=RiskLevel.LOW,
    )
    async def read_file(self, context: PluginContext) -> PluginResult:
        path = context.parameters.get("path", "")
        if not path or not os.path.exists(path):
            return PluginResult.fail(f"File not found: '{path}'")
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return PluginResult.ok(data={"content": content, "size_bytes": len(content)})
        except Exception as err:
            return PluginResult.fail(str(err))

    @capability(
        name="write_file",
        description="Write text content to a file",
        voice_intents=["write file", "save file"],
        risk_level=RiskLevel.MEDIUM,
    )
    async def write_file(self, context: PluginContext) -> PluginResult:
        path = context.parameters.get("path", "")
        content = context.parameters.get("content", "")
        if not path:
            return PluginResult.fail("Path is required")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return PluginResult.ok(data={"status": "written", "path": path, "size": len(content)})
        except Exception as err:
            return PluginResult.fail(str(err))

    @capability(
        name="list_directory",
        description="List files and directories in a folder",
        voice_intents=["list directory", "show files"],
        risk_level=RiskLevel.LOW,
    )
    async def list_directory(self, context: PluginContext) -> PluginResult:
        path = context.parameters.get("path", ".")
        if not os.path.exists(path):
            return PluginResult.fail(f"Directory not found: '{path}'")
        items = os.listdir(path)
        return PluginResult.ok(data={"items": items, "count": len(items)})

    @capability(
        name="file_info",
        description="Get size and metadata of a file",
        voice_intents=["file metadata", "file info"],
        risk_level=RiskLevel.LOW,
    )
    async def file_info(self, context: PluginContext) -> PluginResult:
        path = context.parameters.get("path", "")
        if not path or not os.path.exists(path):
            return PluginResult.fail(f"File not found: '{path}'")
        stat = os.stat(path)
        return PluginResult.ok(data={"size_bytes": stat.st_size, "mtime": stat.st_mtime})
