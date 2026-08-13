"""Python AST Parser extracting classes, methods, variables, and imports.
"""

import ast
from typing import Any, Dict, List, Optional

from app.agents.software_engineer.intelligence.interfaces import ASTParser
from app.agents.software_engineer.intelligence.models import (
    ClassInfo,
    ConstantInfo,
    FunctionInfo,
    ImportInfo,
    MethodInfo,
    Symbol,
    VariableInfo,
)
from app.agents.software_engineer.intelligence.utils import clean_docstring, get_source_snippet


class PythonASTVisitor(ast.NodeVisitor):
    """AST NodeVisitor extracting details about Python modules and definitions."""

    def __init__(self, file_path: str, root_path: str, source_code: str) -> None:
        self.file_path = file_path
        self.root_path = root_path
        self.source_code = source_code

        # Determine module name based on file path, e.g. app/main.py -> app.main
        rel_path = os.path.relpath(file_path, root_path)
        base_name, _ = os.path.splitext(rel_path)
        self.module_name = base_name.replace(os.sep, ".").replace("/", ".")

        self.scope_stack: List[str] = [self.module_name]

        self.symbols: List[Symbol] = []
        self.classes: List[ClassInfo] = []
        self.functions: List[FunctionInfo] = []
        self.methods: List[MethodInfo] = []
        self.imports: List[ImportInfo] = []
        self.variables: List[VariableInfo] = []
        self.constants: List[ConstantInfo] = []

    @property
    def current_scope(self) -> str:
        return ".".join(self.scope_stack)

    def _get_decorators(self, decorator_list: List[ast.expr]) -> List[str]:
        decorators = []
        for dec in decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(ast.unparse(dec))
            elif isinstance(dec, ast.Call):
                decorators.append(ast.unparse(dec.func))
        return decorators

    def _get_parameters(self, args: ast.arguments) -> List[str]:
        params = []
        # Handle standard args
        for arg in args.args:
            annotation = f": {ast.unparse(arg.annotation)}" if arg.annotation else ""
            params.append(f"{arg.arg}{annotation}")
        # Handle kwonly args
        for arg in args.kwonlyargs:
            annotation = f": {ast.unparse(arg.annotation)}" if arg.annotation else ""
            params.append(f"{arg.arg}{annotation}")
        return params

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(
                ImportInfo(
                    module_name=alias.name,
                    imported_name="",
                    alias=alias.asname,
                    file_path=self.file_path,
                    line_number=node.lineno,
                )
            )
            # Register as Symbol
            fqn = f"{self.module_name}.{alias.asname or alias.name}"
            self.symbols.append(
                Symbol(
                    id=f"{fqn}:{self.file_path}",
                    name=alias.asname or alias.name,
                    fully_qualified_name=fqn,
                    symbol_type="import",
                    parent_scope=self.current_scope,
                    module=self.module_name,
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column_number=node.col_offset,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        mod = node.module or ""
        for alias in node.names:
            self.imports.append(
                ImportInfo(
                    module_name=mod,
                    imported_name=alias.name,
                    alias=alias.asname,
                    is_relative=node.level > 0,
                    level=node.level,
                    file_path=self.file_path,
                    line_number=node.lineno,
                )
            )
            # Register as Symbol
            name = alias.asname or alias.name
            fqn = f"{self.module_name}.{name}"
            self.symbols.append(
                Symbol(
                    id=f"{fqn}:{self.file_path}",
                    name=name,
                    fully_qualified_name=fqn,
                    symbol_type="import",
                    parent_scope=self.current_scope,
                    module=self.module_name,
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column_number=node.col_offset,
                )
            )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_name = node.name
        fqn = f"{self.current_scope}.{class_name}"

        # Get parent scope
        parent_scope = self.current_scope
        self.scope_stack.append(class_name)

        bases = [ast.unparse(b) for b in node.bases]
        decorators = self._get_decorators(node.decorator_list)
        docstring = clean_docstring(ast.get_docstring(node))

        # Save class details
        class_info = ClassInfo(
            name=class_name,
            fully_qualified_name=fqn,
            bases=bases,
            decorators=decorators,
            docstring=docstring,
            file_path=self.file_path,
            line_number=node.lineno,
        )
        self.classes.append(class_info)

        # Register Symbol
        snippet = get_source_snippet(self.source_code, node.lineno, node.end_lineno)
        self.symbols.append(
            Symbol(
                id=f"{fqn}:{self.file_path}",
                name=class_name,
                fully_qualified_name=fqn,
                symbol_type="class",
                parent_scope=parent_scope,
                module=self.module_name,
                file_path=self.file_path,
                line_number=node.lineno,
                column_number=node.col_offset,
                end_line=node.end_lineno,
                end_column=node.end_col_offset,
                docstring=docstring,
                signature=f"class {class_name}({', '.join(bases)})",
                source_snippet=snippet,
            )
        )

        # Visit class bodies
        self.generic_visit(node)

        self.scope_stack.pop()

    def _visit_function(self, node: Any, is_async: bool) -> None:
        func_name = node.name
        fqn = f"{self.current_scope}.{func_name}"

        parent_scope = self.current_scope
        self.scope_stack.append(func_name)

        params = self._get_parameters(node.args)
        ret_type = ast.unparse(node.returns) if node.returns else None
        decorators = self._get_decorators(node.decorator_list)
        docstring = clean_docstring(ast.get_docstring(node))

        # Check if it is a method or function (by looking at stack size/parent)
        is_method = len(self.scope_stack) > 2 and self.scope_stack[-2] in [c.name for c in self.classes]

        snippet = get_source_snippet(self.source_code, node.lineno, node.end_lineno)
        sig = f"def {func_name}({', '.join(params)})"
        if ret_type:
            sig += f" -> {ret_type}"

        symbol_node = Symbol(
            id=f"{fqn}:{self.file_path}",
            name=func_name,
            fully_qualified_name=fqn,
            symbol_type="method" if is_method else "function",
            parent_scope=parent_scope,
            module=self.module_name,
            file_path=self.file_path,
            line_number=node.lineno,
            column_number=node.col_offset,
            end_line=node.end_lineno,
            end_column=node.end_col_offset,
            docstring=docstring,
            signature=sig,
            source_snippet=snippet,
        )
        self.symbols.append(symbol_node)

        if is_method:
            parent_class = self.scope_stack[-2]
            method_info = MethodInfo(
                name=func_name,
                class_name=parent_class,
                fully_qualified_name=fqn,
                is_async=is_async,
                parameters=params,
                return_type=ret_type,
                decorators=decorators,
                docstring=docstring,
                file_path=self.file_path,
                line_number=node.lineno,
            )
            self.methods.append(method_info)
            # Find class and add method
            for c in self.classes:
                if c.name == parent_class:
                    c.methods.append(method_info)
        else:
            self.functions.append(
                FunctionInfo(
                    name=func_name,
                    fully_qualified_name=fqn,
                    is_async=is_async,
                    parameters=params,
                    return_type=ret_type,
                    decorators=decorators,
                    docstring=docstring,
                    file_path=self.file_path,
                    line_number=node.lineno,
                )
            )

        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node, is_async=True)

    def visit_Assign(self, node: ast.Assign) -> None:
        # Detect global/local variables or constants
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id
                fqn = f"{self.current_scope}.{name}"
                is_constant = name.isupper() and len(name) > 1

                # Filter out standard temp vars
                if name.startswith("_") and not name.startswith("__"):
                    continue

                if is_constant:
                    self.constants.append(
                        ConstantInfo(
                            name=name,
                            fully_qualified_name=fqn,
                            value_snippet=ast.unparse(node.value),
                            file_path=self.file_path,
                            line_number=node.lineno,
                        )
                    )
                else:
                    self.variables.append(
                        VariableInfo(
                            name=name,
                            fully_qualified_name=fqn,
                            scope=self.current_scope,
                            file_path=self.file_path,
                            line_number=node.lineno,
                        )
                    )

                self.symbols.append(
                    Symbol(
                        id=f"{fqn}:{self.file_path}",
                        name=name,
                        fully_qualified_name=fqn,
                        symbol_type="constant" if is_constant else "variable",
                        parent_scope=self.current_scope,
                        module=self.module_name,
                        file_path=self.file_path,
                        line_number=node.lineno,
                        column_number=node.col_offset,
                        signature=f"{name} = {ast.unparse(node.value)}",
                    )
                )
            elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                # Class attribute assignments, e.g. self.x = 10
                name = target.attr
                # Check if we are inside a method
                if len(self.scope_stack) > 2:
                    fqn = f"{self.current_scope[:-len(self.scope_stack[-1]) - 1]}.{name}"
                    self.variables.append(
                        VariableInfo(
                            name=name,
                            fully_qualified_name=fqn,
                            scope=self.current_scope,
                            file_path=self.file_path,
                            line_number=node.lineno,
                        )
                    )
                    self.symbols.append(
                        Symbol(
                            id=f"{fqn}:{self.file_path}",
                            name=name,
                            fully_qualified_name=fqn,
                            symbol_type="variable",
                            parent_scope=self.current_scope,
                            module=self.module_name,
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column_number=node.col_offset,
                        )
                    )

        self.generic_visit(node)


class PythonASTParser(ASTParser):
    """Implements ASTParser for Python source code using python standard ast visitor."""

    def parse_file(self, file_path: str, root_path: str) -> Dict[str, Any]:
        """Loads and parses source code compiling extracted symbols and imports.

        Args:
            file_path: Target python file path.
            root_path: Workspace root path.

        Returns:
            Dictionary containing extracted symbols, classes, functions, etc.
        """
        source = load_file_safely(file_path)
        try:
            tree = ast.parse(source, filename=file_path)
        except Exception as e:
            # Raise custom ASTParsingError
            from app.agents.software_engineer.intelligence.exceptions import ASTParsingError

            raise ASTParsingError(f"Failed to parse python AST for '{file_path}': {str(e)}") from e

        visitor = PythonASTVisitor(file_path, root_path, source)
        visitor.visit(tree)

        # Return visitor attributes as dict
        return {
            "symbols": visitor.symbols,
            "classes": visitor.classes,
            "functions": visitor.functions,
            "methods": visitor.methods,
            "imports": visitor.imports,
            "variables": visitor.variables,
            "constants": visitor.constants,
            "raw_ast": tree,
        }


import os
