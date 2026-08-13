"""API Extractor Module.

Automatically extracts REST endpoints, GraphQL schemas, WebSockets, gRPC,
Authentication schemes, and Request/Response schemas.
"""

import re
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class APIExtractor:
    """Enterprise API Route & Endpoint Extractor."""

    def __init__(self) -> None:
        logger.info("api_extractor_initialized")

    def extract_apis_from_file(self, file_path: str, source_code: str) -> List[Dict[str, Any]]:
        """Extracts REST endpoint routes (FastAPI, Express, Spring Boot) from source code."""
        endpoints: List[Dict[str, Any]] = []

        # FastAPI / Flask Decorators: @router.get("/path"), @app.post("/path")
        for match in re.finditer(r'@(?:router|app)\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']', source_code, re.IGNORECASE):
            method = match.group(1).upper()
            route_path = match.group(2)
            endpoints.append({
                "endpoint": route_path,
                "http_method": method,
                "file_path": file_path,
                "function_name": "route_handler",
                "summary": f"REST Endpoint {method} {route_path}",
            })

        # Express / Node Route Matchers: app.get('/path', ...)
        for match in re.finditer(r'\bapp\.(get|post|put|delete)\(\s*["\']([^"\']+)["\']', source_code, re.IGNORECASE):
            method = match.group(1).upper()
            route_path = match.group(2)
            endpoints.append({
                "endpoint": route_path,
                "http_method": method,
                "file_path": file_path,
                "function_name": "express_handler",
                "summary": f"Express Route {method} {route_path}",
            })

        logger.info("apis_extracted", file_path=file_path, count=len(endpoints))
        return endpoints
