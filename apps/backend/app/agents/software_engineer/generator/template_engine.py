"""Template Engine providing pre-configured boilerplate skeletons for rapid generation.
"""

from typing import Any, Dict

from app.agents.software_engineer.generator.interfaces import TemplateEngine
from app.agents.software_engineer.generator.utils import resolve_placeholders

DEFAULT_TEMPLATES = {
    "python_module": """\"\"\"{{Description}}
\"\"\"

import logging

logger = logging.getLogger(__name__)


class {{ClassName}}:
    \"\"\"{{ClassDocstring}}
    \"\"\"

    def __init__(self) -> None:
        pass

    def execute(self) -> None:
        pass
""",
    "fastapi_endpoint": """from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

router = APIRouter(prefix="/{{Prefix}}", tags=["{{Tag}}"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_{{EntityLower}}(payload: dict):
    \"\"\"Creates a new {{Entity}} record.
    \"\"\"
    return {"status": "created", "data": payload}


@router.get("/", response_model=List[dict])
async def list_{{EntityLower}}s():
    \"\"\"Lists all {{Entity}} records.
    \"\"\"
    return []
""",
    "pydantic_schema": """from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class {{SchemaName}}Schema(BaseModel):
    \"\"\"Pydantic schema validation for {{SchemaName}}.
    \"\"\"

    id: str = Field(..., description="Unique entity ID.")
    name: str = Field(..., description="Short descriptive name.")
""",
    "dockerfile": """FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv pip install --system -r pyproject.toml

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
}


class CodeTemplateEngine(TemplateEngine):
    """Renders pre-registered or default skeletons substituting placeholders."""

    def __init__(self) -> None:
        self.templates = dict(DEFAULT_TEMPLATES)

    def render(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Renders template substituting placeholders.

        Args:
            template_name: Target template identifier.
            variables: Variable replacements scope mapping.

        Returns:
            Rendered code string.
        """
        tpl = self.templates.get(template_name)
        if not tpl:
            # Return a simple placeholder string if not registered
            return f"# Template '{template_name}' not found."

        return resolve_placeholders(tpl, variables)

    def register_template(self, name: str, template_body: str) -> None:
        """Registers a custom template."""
        self.templates[name] = template_body
