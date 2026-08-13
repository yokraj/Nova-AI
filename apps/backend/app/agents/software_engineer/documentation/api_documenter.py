"""API Documenter generating FastAPI router endpoints documentation schemas.
"""

import ast
import os
from typing import List

from app.agents.software_engineer.documentation.interfaces import APIDocumenter
from app.agents.software_engineer.documentation.models import APIDocument


class FastAPIDocumenter(APIDocumenter):
    """Parses router source files mapping routes and HTTP methods annotations."""

    def document_api(
        self, workspace_path: str, file_path: str
    ) -> List[APIDocument]:
        """Statically inspects endpoints definitions.

        Args:
            workspace_path: Absolute workspace root.
            file_path: Relative file path.

        Returns:
            List of APIDocument.
        """
        docs: List[APIDocument] = []
        abs_path = os.path.join(workspace_path, file_path)

        if not os.path.exists(abs_path):
            return docs

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check decorators, e.g. @router.get(...) or @router.post(...)
                    for dec in node.decorator_list:
                        # Extract decorator call details
                        is_route = False
                        method = "GET"
                        endpoint_path = "/unknown"

                        if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                            if dec.func.attr in ("get", "post", "put", "delete", "patch"):
                                is_route = True
                                method = dec.func.attr.upper()
                                if dec.args and isinstance(dec.args[0], ast.Constant):
                                    endpoint_path = dec.args[0].value

                        if is_route:
                            docs.append(
                                APIDocument(
                                    endpoint=endpoint_path,
                                    method=method,
                                    description=ast.get_docstring(node) or f"FastAPI {method} endpoint.",
                                    auth_required="auth" in content.lower(),
                                )
                            )
        except Exception:
            pass

        return docs
