"""Post-processes generated files, extracting symbols and resolving imports.
"""

import ast
from typing import List

from app.agents.software_engineer.generator.models import (
    GeneratedClass,
    GeneratedFile,
    GeneratedFunction,
)


class CodePostProcessor:
    """Extracts symbols from generated files to construct rich results reports."""

    def post_process(self, file_path: str, content: str) -> GeneratedFile:
        """Parses generated file content to populate class and function definitions list.

        Args:
            file_path: Relative target file path.
            content: Generated code source content.

        Returns:
            GeneratedFile model.
        """
        classes: List[GeneratedClass] = []
        functions: List[GeneratedFunction] = []

        try:
            tree = ast.parse(content, filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [
                        child.name
                        for child in node.body
                        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ]
                    classes.append(
                        GeneratedClass(
                            name=node.name,
                            bases=[ast.unparse(b) for b in node.bases],
                            methods=methods,
                            docstring=ast.get_docstring(node),
                        )
                    )
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Extract only top-level functions (parent is Module)
                    # We check if there is another function or class in scopes parent (simplified walk)
                    # Let's count them if not under a ClassDef
                    is_method = False
                    for parent in ast.walk(tree):
                        if isinstance(parent, ast.ClassDef) and node in parent.body:
                            is_method = True
                            break

                    if not is_method:
                        params = [arg.arg for arg in node.args.args]
                        functions.append(
                            GeneratedFunction(
                                name=node.name,
                                parameters=params,
                                return_type=ast.unparse(node.returns) if node.returns else None,
                                is_async=is_async_def(node),
                                docstring=ast.get_docstring(node),
                            )
                        )
        except Exception:
            pass

        return GeneratedFile(
            file_path=file_path,
            content=content,
            classes=classes,
            functions=functions,
        )


def is_async_def(node: ast.AST) -> bool:
    """Helper to check if function node is async."""
    return isinstance(node, ast.AsyncFunctionDef)
