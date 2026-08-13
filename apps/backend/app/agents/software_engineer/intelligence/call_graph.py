"""Generates static call graphs mapping callers to callees and detecting recursion.
"""

import ast
from typing import Any, Dict, List, Set

from app.agents.software_engineer.intelligence.models import CallGraph


class CallVisitor(ast.NodeVisitor):
    """AST visitor extracting function call targets from a function body."""

    def __init__(self) -> None:
        self.callees: Set[str] = set()

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if isinstance(func, ast.Name):
            self.callees.add(func.id)
        elif isinstance(func, ast.Attribute):
            self.callees.add(func.attr)
        elif isinstance(func, ast.Call):
            # Chains, e.g. get_logger().info()
            if isinstance(func.func, ast.Attribute):
                self.callees.add(func.func.attr)
        self.generic_visit(node)


def build_call_graph(ast_trees: Dict[str, Any], module_symbols: List[Any]) -> CallGraph:
    """Statically resolves call chains.

    Args:
        ast_trees: Dict mapping relative file path to parsed raw AST.
        module_symbols: List of indexed Symbols in workspace.

    Returns:
        CallGraph model.
    """
    calls: Dict[str, List[str]] = {}
    callers: Dict[str, List[str]] = {}
    recursive_calls: List[str] = []

    # Map name or suffix to fully qualified name for lookup resolving
    sym_lookup: Dict[str, str] = {}
    for sym in module_symbols:
        sym_lookup[sym.name] = sym.fully_qualified_name
        sym_lookup[sym.fully_qualified_name] = sym.fully_qualified_name

    # 1. Walk ASTs to find callers
    for file_path, raw_ast in ast_trees.items():
        if not raw_ast:
            continue

        # Simple walk to locate all FunctionDef/AsyncFunctionDef blocks
        for node in ast.walk(raw_ast):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Determine caller qualified name
                # Walk scope upwards or check symbols list
                caller_name = node.name
                caller_fqn = None
                for sym in module_symbols:
                    if sym.file_path == file_path and sym.name == caller_name and sym.line_number == node.lineno:
                        caller_fqn = sym.fully_qualified_name
                        break

                if not caller_fqn:
                    continue  # Safety check

                # Visit body to extract callees
                visitor = CallVisitor()
                for child in node.body:
                    visitor.visit(child)

                calls[caller_fqn] = []
                for target in visitor.callees:
                    # Resolve to fully qualified name
                    resolved_fqn = sym_lookup.get(target)
                    if resolved_fqn:
                        if resolved_fqn not in calls[caller_fqn]:
                            calls[caller_fqn].append(resolved_fqn)
                        # Register recursive call if it calls itself
                        if resolved_fqn == caller_fqn and caller_fqn not in recursive_calls:
                            recursive_calls.append(caller_fqn)

    # 2. Build callers map (callee -> list of callers)
    for src, dests in calls.items():
        for d in dests:
            callers.setdefault(d, []).append(src)

    return CallGraph(
        calls=calls,
        callers=callers,
        recursive_calls=recursive_calls,
    )
