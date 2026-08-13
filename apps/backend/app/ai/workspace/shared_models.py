"""Shared Models endpoint definitions and GPU cluster routing.
"""

from typing import Any, Dict, List


class SharedModels:
    """Manages shared model endpoint definitions and GPU cluster routing across workspace nodes."""

    def list_shared_models(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Returns list of shared local and remote AI models."""
        return [
            {"model_id": "deepseek-coder:6.7b", "provider": "ollama", "node": "GPU_Cluster_Node_1"},
            {"model_id": "qwen2.5-vl:7b", "provider": "ollama", "node": "GPU_Cluster_Node_2"},
        ]
