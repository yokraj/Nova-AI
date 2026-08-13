"""Version Tracker logging generated files timestamps and SHA configuration logs.
"""

import hashlib
import time
from app.agents.software_engineer.documentation.interfaces import VersionTracker
from app.agents.software_engineer.documentation.models import DocumentationVersion


class DocumentationVersionTracker(VersionTracker):
    """Tracks document version logs."""

    def track_version(
        self, doc_type: str, file_path: str, content: str
    ) -> DocumentationVersion:
        """Saves version mapping stats.

        Args:
            doc_type: Type category of the document.
            file_path: Absolute or relative target path.
            content: Document content string.

        Returns:
            DocumentationVersion.
        """
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        return DocumentationVersion(
            version_id="1.0.0",
            doc_type=doc_type,
            file_path=file_path,
            hash_value=content_hash,
            timestamp=time.time(),
        )
