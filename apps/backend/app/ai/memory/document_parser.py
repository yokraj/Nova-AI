"""Document Parser extracts structural metadata and formats content.
"""

import os
from typing import Dict, Any

class DocumentParser:
    """Parses raw text configurations and detects coding language mappings."""

    def parse(self, loaded_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Resolves file paths to clean source paths, language types, and textual contents."""
        path = loaded_doc["filepath"]
        ext = loaded_doc["extension"]
        content = loaded_doc["content"]

        # Map extensions to programming languages
        language_mapping = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".md": "markdown",
            ".txt": "text",
            ".json": "json"
        }
        language = language_mapping.get(ext, "unknown")

        return {
            "source": path,
            "filename": os.path.basename(path),
            "language": language,
            "content": content,
            "metadata": {
                "source": path,
                "language": language,
                "size_bytes": loaded_doc["size_bytes"]
            }
        }
