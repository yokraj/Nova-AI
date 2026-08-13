"""Explorer Controller implements local file explorer and filesystem manipulations.
"""

import structlog
import os
import shutil
import glob
from typing import List, Optional, Any

from app.ai.automation.interfaces import ExplorerController as IExplorerController

logger = structlog.get_logger("explorer_controller")

class ExplorerController(IExplorerController):
    """Executes filesystem folder and file modifications with dry-run safe flags."""

    def __init__(self, provider: Any = None) -> None:
        self.provider = provider

    def open_directory(self, path: str) -> None:
        """Opens directory inside OS visual file explorer manager."""
        logger.info("Opening explorer directory view", path=path)
        is_mock = getattr(self.provider, "is_mock", True)
        if not is_mock:
            try:
                os.startfile(path)
            except Exception as err:
                logger.warning("os.startfile not supported or failed", path=path, error=str(err))

    def open_file(self, path: str) -> None:
        """Launches file handler registered on the system."""
        logger.info("Opening document file", path=path)
        is_mock = getattr(self.provider, "is_mock", True)
        if not is_mock:
            try:
                os.startfile(path)
            except Exception as err:
                logger.warning("os.startfile failed for document", path=path, error=str(err))

    def create_folder(self, path: str) -> None:
        """Creates target directory path if missing."""
        logger.info("Creating directory", path=path)
        is_mock = getattr(self.provider, "is_mock", True)
        if not is_mock:
            os.makedirs(path, exist_ok=True)

    def rename(self, path: str, new_name: str) -> None:
        """Renames path folder or file target."""
        logger.info("Renaming path", path=path, new_name=new_name)
        is_mock = getattr(self.provider, "is_mock", True)
        if not is_mock:
            parent = os.path.dirname(path)
            dest = os.path.join(parent, new_name)
            os.rename(path, dest)

    def move(self, path: str, destination: str) -> None:
        """Moves source target to destination."""
        logger.info("Moving file/folder", path=path, destination=destination)
        is_mock = getattr(self.provider, "is_mock", True)
        if not is_mock:
            shutil.move(path, destination)

    def copy(self, path: str, destination: str) -> None:
        """Duplicates folder or file to target destination path."""
        logger.info("Copying file/folder", path=path, destination=destination)
        is_mock = getattr(self.provider, "is_mock", True)
        if not is_mock:
            if os.path.isdir(path):
                shutil.copytree(path, destination)
            else:
                shutil.copy(path, destination)

    def delete(self, path: str) -> None:
        """Deletes target file or directory recursively."""
        logger.info("Deleting file/folder", path=path)
        is_mock = getattr(self.provider, "is_mock", True)
        if not is_mock:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)

    def search(self, root: str, pattern: str) -> List[str]:
        """Runs folder recursive matching scan search."""
        logger.info("Scanning directory contents", root=root, pattern=pattern)
        is_mock = getattr(self.provider, "is_mock", True)
        if is_mock:
            return [os.path.join(root, "mock_match.txt")]

        try:
            search_path = os.path.join(root, "**", pattern)
            return glob.glob(search_path, recursive=True)
        except Exception:
            return []
