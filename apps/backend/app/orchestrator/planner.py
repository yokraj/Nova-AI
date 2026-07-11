"""TaskPlanner planning, splitting, and merging coordinated agent tasks.
"""

from typing import Any, Dict, List
from app.orchestrator.intent import IntentType


class TaskPlanner:
    """Plans, splits, and merges coordinator task stages."""

    def create_plan(self, intent: IntentType, prompt: str) -> List[Dict[str, Any]]:
        """Creates a list of task steps based on intent classification and prompt.

        Args:
            intent: Classified IntentType.
            prompt: Input query prompt.

        Returns:
            List of tasks dicts.
        """
        if intent == IntentType.CODE:
            return [
                {"id": "write_code", "agent_name": "CodeAgent", "prompt": f"Write code for: {prompt}"},
                {"id": "test_code", "agent_name": "CodeAgent", "prompt": "Test code generated"},
            ]
        elif intent == IntentType.WORKFLOW:
            return [
                {"id": "step_1", "agent_name": "WorkflowAgent", "prompt": "Initialize workflow"},
                {"id": "step_2", "agent_name": "WorkflowAgent", "prompt": f"Execute workflow payload: {prompt}"},
            ]

        agent_name = "ChatAgent"
        if intent == IntentType.SEARCH:
            agent_name = "SearchAgent"
        elif intent == IntentType.BROWSER:
            agent_name = "BrowserAgent"
        elif intent == IntentType.DESKTOP:
            agent_name = "DesktopAgent"
        elif intent == IntentType.VOICE:
            agent_name = "VoiceAgent"
        elif intent == IntentType.VISION:
            agent_name = "VisionAgent"

        return [{"id": "single_step", "agent_name": agent_name, "prompt": prompt}]

    def split(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Splits a single complex task into simpler concurrent sub-tasks.

        Args:
            task: Task dictionary.

        Returns:
            List of split sub-task dictionaries.
        """
        task_id = task.get("id", "task")
        prompt = task.get("prompt", "")
        agent_name = task.get("agent_name", "ChatAgent")

        return [
            {"id": f"{task_id}_part1", "agent_name": agent_name, "prompt": f"Phase 1: {prompt}"},
            {"id": f"{task_id}_part2", "agent_name": agent_name, "prompt": f"Phase 2: {prompt}"},
        ]

    def merge(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merges multiple tasks/results into a single consolidated summary.

        Args:
            tasks: List of task outputs/results.

        Returns:
            Consolidated task dictionary.
        """
        merged_output = "\n".join([str(t.get("output", "")) for t in tasks])
        return {
            "id": "merged_result",
            "output": merged_output,
            "success": all(t.get("success", False) for t in tasks),
        }
