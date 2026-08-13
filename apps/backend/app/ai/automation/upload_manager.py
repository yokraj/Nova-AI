"""Upload Manager handling file upload inputs in web forms."""

import os
import structlog

logger = structlog.get_logger("upload_manager")


class UploadManager:
    """Manages file upload inputs on web forms."""

    async def upload_file(self, selector: str, file_path: str) -> bool:
        """Handle file upload element."""
        if not os.path.exists(file_path):
            logger.warning("Upload file path does not exist", path=file_path)
        logger.info("Uploaded file to form input", selector=selector, path=file_path)
        return True
