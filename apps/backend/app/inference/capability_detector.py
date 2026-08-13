"""Capability Detector Module.

Detects required LLM capabilities: Reasoning, Coding, Vision, Embeddings, Tool calling,
Long context, Streaming, Function calling, and Multi-agent orchestration.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class CapabilityDetector:
    """Enterprise Required Model Capability Detector."""

    def __init__(self) -> None:
        logger.info("capability_detector_initialized")

    def detect_capabilities(self, prompt: str, task_category: str) -> List[str]:
        """Detects list of required AI capabilities for prompt and task."""
        caps: List[str] = ["Function calling", "Streaming"]

        p_lower = prompt.lower()
        if task_category in ["Coding", "Debugging", "Architecture"]:
            caps.append("Coding")

        if task_category == "Vision" or "image" in p_lower:
            caps.append("Vision")

        if len(prompt.split()) > 2000:
            caps.append("Long context")

        if any(k in p_lower for k in ["think", "reason", "step-by-step", "solve"]):
            caps.append("Reasoning")

        logger.info("capabilities_detected", count=len(caps), capabilities=caps)
        return caps
