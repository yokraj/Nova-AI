"""ResponseBuilder aggregating and formatting agent output data.
"""

from typing import Any, Dict, List


class ResponseBuilder:
    """Aggregates, summarizes, and formats responses."""

    def aggregate(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates multiple agent execution responses.

        Args:
            responses: List of raw output responses dicts.

        Returns:
            Dict containing aggregated results.
        """
        success = all(r.get("success", False) for r in responses)
        collected = []
        for r in responses:
            out = r.get("output") or r.get("response") or ""
            collected.append(str(out))
        return {"success": success, "outputs": collected, "count": len(responses)}

    def summarize(self, data: Dict[str, Any]) -> str:
        """Summarizes aggregated outcomes into unified response content.

        Args:
            data: Aggregated data dictionary.

        Returns:
            Summary string content.
        """
        count = data.get("count", 0)
        success = data.get("success", False)
        outputs = data.get("outputs", [])

        status = "Success" if success else "Failure"
        joined = "\n\n".join(outputs)
        return f"Orchestrator Execution Status: {status} (Aggregated {count} steps)\n\n{joined}"

    def format(self, text: str, format_type: str = "markdown") -> str:
        """Applies format layouts to response string.

        Args:
            text: Plain text input.
            format_type: Target layout layout (e.g. 'markdown', 'html', 'json').

        Returns:
            Formatted response string.
        """
        if format_type.lower() == "markdown":
            return f"### Response\n\n{text}"
        elif format_type.lower() == "json":
            import json

            return json.dumps({"response": text})
        return text
