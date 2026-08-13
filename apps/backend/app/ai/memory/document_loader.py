"""Document Loader loads files from disk.
"""

import os
from typing import List, Dict, Any
from app.ai.memory.exceptions import DocumentProcessingError

class DocumentLoader:
    """Discovers and reads project documents matching code and documentation extensions."""

    def load_file(self, filepath: str) -> Dict[str, Any]:
        """Reads file content and collects file info."""
        if not os.path.exists(filepath):
            raise DocumentProcessingError(f"File not found: {filepath}")

        try:
            # Check size limits
            stat = os.stat(filepath)
            size_mb = stat.st_size / (1024 * 1024)
            if size_mb > 10.0:
                raise DocumentProcessingError(f"File exceeds size limit: {filepath}")

            # Basic textual load
            ext = os.path.splitext(filepath)[1].lower()
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            return {
                "filepath": filepath,
                "content": content,
                "extension": ext,
                "size_bytes": stat.st_size
            }
        except Exception as err:
            raise DocumentProcessingError(f"Failed to read file '{filepath}': {err}")

    def load_directory(self, dirpath: str, extensions: List[str]) -> List[Dict[str, Any]]:
        """Scans a directory recursively and loads matching files."""
        results = []
        if not os.path.isdir(dirpath):
            return results

        for root, _, files in os.walk(dirpath):
            # Ignore hidden dirs or pycaches
            if ".git" in root or "__pycache__" in root or ".nova" in root:
                continue

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in extensions:
                    path = os.path.join(root, file)
                    try:
                        results.append(self.load_file(path))
                    except Exception:
                        pass
        return results
