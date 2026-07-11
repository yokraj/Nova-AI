"""PromptLoader loading templates from YAML, JSON, and Markdown formats.
"""

import json
from typing import Any, Dict

from app.agent_sdk.prompt.exceptions import PromptLoadingError
from app.agent_sdk.prompt.prompt import Prompt


def _parse_yaml(content: str) -> Dict[str, Any]:
    """Custom parser for simple YAML key-value blocks to avoid external dependencies."""
    result = {}
    lines = content.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()

        # Parse lists
        if val.startswith("[") and val.endswith("]"):
            val_clean = val[1:-1].strip()
            if not val_clean:
                result[key] = []
            else:
                result[key] = [item.strip() for item in val_clean.split(",")]
        # Parse dictionaries/json
        elif val.startswith("{") and val.endswith("}"):
            try:
                result[key] = json.loads(val.replace("'", '"'))
            except Exception:
                result[key] = {}
        # Parse quotes
        elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val_clean = val[1:-1]
            val_clean = val_clean.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
            result[key] = val_clean
        else:
            result[key] = val
    return result


class PromptLoader:
    """Loads prompt templates from Markdown, YAML, and JSON files."""

    def load_from_yaml(self, file_path: str) -> Prompt:
        """Loads prompt from a YAML file.

        Args:
            file_path: Absolute file path.

        Returns:
            Instantiated Prompt object.

        Raises:
            PromptLoadingError: If loading or parsing fails.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            data = _parse_yaml(content)
            return Prompt(**data)
        except Exception as e:
            raise PromptLoadingError(f"Failed to load YAML prompt: {str(e)}") from e

    def load_from_json(self, file_path: str) -> Prompt:
        """Loads prompt from a JSON file.

        Args:
            file_path: Absolute file path.

        Returns:
            Instantiated Prompt object.

        Raises:
            PromptLoadingError: If loading or parsing fails.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Prompt(**data)
        except Exception as e:
            raise PromptLoadingError(f"Failed to load JSON prompt: {str(e)}") from e

    def load_from_markdown(self, file_path: str) -> Prompt:
        """Loads prompt from a Markdown file containing YAML frontmatter.

        Args:
            file_path: Absolute file path.

        Returns:
            Instantiated Prompt object.

        Raises:
            PromptLoadingError: If loading or parsing fails.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.startswith("---"):
                raise PromptLoadingError("Markdown prompt file must start with YAML frontmatter delimiter '---'.")

            parts = content.split("---", 2)
            if len(parts) < 3:
                raise PromptLoadingError("Markdown prompt file contains invalid frontmatter blocks.")

            frontmatter = _parse_yaml(parts[1])
            body = parts[2].strip()

            system_prompt = ""
            user_prompt = ""

            if "# System Prompt" in body and "# User Prompt" in body:
                body_parts = body.split("# User Prompt", 1)
                system_part = body_parts[0].replace("# System Prompt", "").strip()
                user_part = body_parts[1].strip()
                system_prompt = system_part
                user_prompt = user_part
            else:
                user_prompt = body

            frontmatter["system_prompt"] = system_prompt
            frontmatter["user_prompt"] = user_prompt

            return Prompt(**frontmatter)
        except Exception as e:
            raise PromptLoadingError(f"Failed to load Markdown prompt: {str(e)}") from e
