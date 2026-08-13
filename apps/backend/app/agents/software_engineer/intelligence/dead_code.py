"""Analyzes call graphs and AST structures to identify dead or unused code.
"""

import ast
from typing import Any, Dict, List, Set

from app.agents.software_engineer.intelligence.interfaces import DeadCodeAnalyzer
from app.agents.software_engineer.intelligence.models import (
    CallGraph,
    ClassInfo,
    ConstantInfo,
    DeadCodeReport,
    FunctionInfo,
    ImportInfo,
    MethodInfo,
    Symbol,
    VariableInfo,
)


class ASTUsageVisitor(ast.NodeVisitor):
    """AST visitor tracking all loaded variable and attribute identifiers."""

    def __init__(self) -> None:
        self.loaded_names: Set[str] = set()

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self.loaded_names.add(node.id)
        self.generic_visit(node)


class ASTDeadCodeAnalyzer(DeadCodeAnalyzer):
    """Detects dead code definitions by verifying usage links and references."""

    def find_dead_code(
        self,
        files: List[str],
        symbols: Dict[str, Symbol],
        imports: Dict[str, List[ImportInfo]],
        call_graph: CallGraph,
    ) -> DeadCodeReport:
        """Analyzes active usage references to locate unused or unreachable code definitions.

        Args:
            files: Relative paths of all files.
            symbols: Domain symbols mapped by fully qualified name.
            imports: Mapping of relative path to list of imports in that file.
            call_graph: Complete CallGraph of the workspace.

        Returns:
            DeadCodeReport model.
        """
        unused_imports: List[ImportInfo] = []
        unused_functions: List[FunctionInfo] = []
        unused_methods: List[MethodInfo] = []
        unused_classes: List[ClassInfo] = []
        unused_variables: List[VariableInfo] = []
        unused_constants: List[ConstantInfo] = []

        # 1. Unused global/local variables inside each file's AST
        # To keep it simple and robust, we check references list of symbols.
        # If a symbol is a variable, constant, class, function, or method,
        # and it has 0 references, it is potentially dead!
        # Exceptions: main entrypoints or standard exported names (like dunders __init__, etc.)
        for fqn, sym in symbols.items():
            # Skip module/import/dunder symbols
            if sym.symbol_type in ("module", "import") or sym.name.startswith("__"):
                continue

            # Check if it has any references
            has_refs = len(sym.references) > 0

            # Double check Call Graph for executable nodes (functions/methods)
            is_called = fqn in call_graph.callers

            if not has_refs and not is_called:
                # Classify unused symbol
                if sym.symbol_type == "function":
                    unused_functions.append(
                        FunctionInfo(
                            name=sym.name,
                            fully_qualified_name=fqn,
                            file_path=sym.file_path,
                            line_number=sym.line_number,
                        )
                    )
                elif sym.symbol_type == "method":
                    # Keep class method structure
                    unused_methods.append(
                        MethodInfo(
                            name=sym.name,
                            class_name=sym.parent_scope.split(".")[-1],
                            fully_qualified_name=fqn,
                            file_path=sym.file_path,
                            line_number=sym.line_number,
                        )
                    )
                elif sym.symbol_type == "class":
                    unused_classes.append(
                        ClassInfo(
                            name=sym.name,
                            fully_qualified_name=fqn,
                            file_path=sym.file_path,
                            line_number=sym.line_number,
                        )
                    )
                elif sym.symbol_type == "variable":
                    unused_variables.append(
                        VariableInfo(
                            name=sym.name,
                            fully_qualified_name=fqn,
                            scope=sym.parent_scope,
                            file_path=sym.file_path,
                            line_number=sym.line_number,
                        )
                    )
                elif sym.symbol_type == "constant":
                    unused_constants.append(
                        ConstantInfo(
                            name=sym.name,
                            fully_qualified_name=fqn,
                            file_path=sym.file_path,
                            line_number=sym.line_number,
                        )
                    )

        # 2. Unused imports (file-level analysis)
        # Check if imported names are used in the same file's code
        # We can find all imports per file and see if they appear in references or ast
        for file_path, imp_list in imports.items():
            for imp in imp_list:
                name_to_check = imp.alias or imp.imported_name or imp.module_name.split(".")[-1]
                # If name_to_check is not referenced in the file (after definition line), it's unused
                # A quick look at references:
                is_used = False
                for fqn, sym in symbols.items():
                    if sym.file_path == file_path and name_to_check in sym.references:
                        is_used = True
                        break
                if not is_used:
                    unused_imports.append(imp)

        return DeadCodeReport(
            unused_imports=unused_imports,
            unused_functions=unused_functions,
            unused_methods=unused_methods,
            unused_classes=unused_classes,
            unused_variables=unused_variables,
            unused_constants=unused_constants,
        )
