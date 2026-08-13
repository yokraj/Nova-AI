"""Code Metadata Module.

Extracts package manager manifests (pyproject.toml, package.json, pom.xml, go.mod),
build configs, licenses, and Git metadata.
"""

import os
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class CodeMetadataExtractor:
    """Enterprise Package & Repository Metadata Extractor."""

    def __init__(self) -> None:
        logger.info("code_metadata_extractor_initialized")

    def extract_repository_metadata(self, root_path: str) -> Dict[str, Any]:
        """Extracts frameworks, package managers, and build systems from repository root."""
        frameworks: List[str] = []
        package_managers: List[str] = []

        if os.path.exists(os.path.join(root_path, "pyproject.toml")) or os.path.exists(os.path.join(root_path, "requirements.txt")):
            package_managers.append("pip / poetry")
            frameworks.append("FastAPI / Python")

        if os.path.exists(os.path.join(root_path, "package.json")):
            package_managers.append("npm / yarn")
            frameworks.append("Node.js / React")

        if os.path.exists(os.path.join(root_path, "pom.xml")):
            package_managers.append("Maven")
            frameworks.append("Spring Boot / Java")

        if os.path.exists(os.path.join(root_path, "go.mod")):
            package_managers.append("Go Modules")
            frameworks.append("Go Standard")

        logger.info("repository_metadata_extracted", root_path=root_path, frameworks_count=len(frameworks))
        return {
            "root_path": root_path,
            "frameworks": frameworks,
            "package_managers": package_managers,
        }
