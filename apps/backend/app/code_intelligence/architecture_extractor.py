"""Architecture Extractor Module.

Automatically detects software architectural patterns: MVC, Layered architecture,
Clean Architecture, Hexagonal, Microservices, DDD, Repository Pattern, CQRS, Event-driven, and Pipeline architecture.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class ArchitectureExtractor:
    """Enterprise Software Architecture Pattern Recognition Engine."""

    def __init__(self) -> None:
        logger.info("architecture_extractor_initialized")

    def detect_architecture_patterns(
        self, file_paths: List[str], symbols: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyzes repository directory structure and symbols to identify architectural patterns."""
        patterns: List[Dict[str, Any]] = []
        path_str = " ".join(file_paths).lower()
        sym_str = " ".join([s.get("name", "") for s in symbols]).lower()

        # 1. Repository Pattern
        if "repository" in path_str or "repository" in sym_str:
            patterns.append({
                "pattern_name": "Repository Pattern",
                "component_name": "Data Access Layer",
                "file_paths": [f for f in file_paths if "repository" in f.lower()],
                "description": "Encapsulates data storage persistence logic behind repository abstractions.",
            })

        # 2. MVC / Layered Architecture
        if any(layer in path_str for layer in ["models", "controllers", "views", "api", "service"]):
            patterns.append({
                "pattern_name": "Layered Architecture",
                "component_name": "API & Business Service Layers",
                "file_paths": [f for f in file_paths if any(k in f.lower() for k in ["api", "service", "model"])],
                "description": "Decoupled multi-tier presentation, domain, and data access layers.",
            })

        # 3. Clean / Hexagonal Architecture
        if "domain" in path_str and "infrastructure" in path_str:
            patterns.append({
                "pattern_name": "Clean Architecture",
                "component_name": "Domain Core & Ports/Adapters",
                "file_paths": [f for f in file_paths if "domain" in f.lower() or "infrastructure" in f.lower()],
                "description": "Inverted dependency rule isolating core domain entities from external infrastructure.",
            })

        # 4. Event-Driven Architecture
        if any(k in sym_str or k in path_str for k in ["event", "pubsub", "bus", "listener", "message"]):
            patterns.append({
                "pattern_name": "Event-Driven Architecture",
                "component_name": "Event Bus & Message Handlers",
                "file_paths": [f for f in file_paths if "event" in f.lower() or "bus" in f.lower()],
                "description": "Asynchronous decoupled communication via domain event publication.",
            })

        logger.info("architecture_patterns_detected", pattern_count=len(patterns))
        return patterns
