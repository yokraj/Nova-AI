"""Download Manager managing browser download interception and local destination saving."""

import os
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger("download_manager")


class DownloadManager:
    """Intercepts and manages file downloads from web pages."""

    def __init__(self, download_dir: str = "./data/downloads") -> None:
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
        self._downloads: List[Dict[str, Any]] = []

    async def handle_download(self, url: str, filename: str) -> str:
        """Simulate downloading file to target directory."""
        target_path = os.path.join(self.download_dir, filename)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(f"Sample downloaded file payload from {url}")

        record = {"url": url, "filename": filename, "path": target_path, "status": "completed"}
        self._downloads.append(record)
        logger.info("Intercepted and saved file download", url=url, path=target_path)
        return target_path

    async def list_downloads(self) -> List[Dict[str, Any]]:
        """List tracked downloads."""
        return list(self._downloads)
