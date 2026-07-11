"""PromptTemplate facade encapsulating file system loaders, rendering, and validations.
"""

import os
from typing import Any, Dict

from app.agent_sdk.prompt.prompt import Prompt
from app.agent_sdk.prompt.loader import PromptLoader
from app.agent_sdk.prompt.renderer import PromptRenderer
from app.agent_sdk.prompt.validator import PromptValidator


def _dump_yaml(data: Dict[str, Any]) -> str:
    """Custom serializer for simple key-value YAML blocks to avoid external dependencies."""
    import json
    lines = []
    for k, v in data.items():
        if isinstance(v, list):
            items_str = ", ".join(str(item) for item in v)
            lines.append(f"{k}: [{items_str}]")
        elif isinstance(v, dict):
            lines.append(f"{k}: {json.dumps(v)}")
        else:
            val_escaped = str(v).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
            lines.append(f'{k}: "{val_escaped}"')
    return "\n".join(lines) + "\n"


class PromptTemplate:
    """Main facade representing loaded prompt templates with lifecycle operations."""

    def __init__(self) -> None:
        """Initializes PromptTemplate."""
        self.loader = PromptLoader()
        self.renderer = PromptRenderer()
        self.validator = PromptValidator()

    def load(self, file_path: str) -> Prompt:
        """Loads prompt templates from file.

        Args:
            file_path: Absolute file path.

        Returns:
            Loaded Prompt instance.

        Raises:
            ValueError: If file extension is unsupported.
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext in (".yaml", ".yml"):
            return self.loader.load_from_yaml(file_path)
        elif ext == ".json":
            return self.loader.load_from_json(file_path)
        elif ext in (".md", ".markdown"):
            return self.loader.load_from_markdown(file_path)
        else:
            raise ValueError(f"Unsupported prompt template file extension: {ext}")

    def save(self, file_path: str, prompt: Prompt) -> None:
        """Persists prompt template configuration to disk.

        Args:
            file_path: Absolute target file path.
            prompt: Prompt definition to persist.

        Raises:
            ValueError: If target format extension is unsupported.
        """
        ext = os.path.splitext(file_path)[1].lower()
        data = prompt.model_dump()

        if ext in (".yaml", ".yml"):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(_dump_yaml(data))
        elif ext == ".json":
            import json

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        elif ext in (".md", ".markdown"):
            frontmatter_dict = {
                k: v for k, v in data.items() if k not in ("system_prompt", "user_prompt")
            }
            frontmatter_dict["id"] = str(frontmatter_dict["id"])
            frontmatter_yaml = _dump_yaml(frontmatter_dict)
            content = (
                f"---\n{frontmatter_yaml}---\n\n"
                f"# System Prompt\n{prompt.system_prompt}\n\n"
                f"# User Prompt\n{prompt.user_prompt}\n"
            )
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            raise ValueError(f"Unsupported prompt template serialization extension: {ext}")

    def render(self, prompt: Prompt, variables: Dict[str, Any]) -> str:
        """Renders the prompt templates with runtime variables, returning the user prompt content.

        Args:
            prompt: Prompt definition.
            variables: Dict of variable keys and values.

        Returns:
            Rendered prompt content.
        """
        return self.renderer.render(prompt.user_prompt, variables)

    def validate(self, prompt: Prompt, variables: Dict[str, Any]) -> bool:
        """Validates the prompt templates against runtime variables.

        Args:
            prompt: Prompt definition.
            variables: Dict of variables to check.

        Returns:
            True if valid; raises exception otherwise.
        """
        self.validator.validate(prompt, variables)
        return True
