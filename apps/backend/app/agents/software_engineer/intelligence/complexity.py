"""Calculates cyclomatic complexity and cognitive complexity metrics.
"""

import ast
from typing import Optional

from app.agents.software_engineer.intelligence.interfaces import ComplexityAnalyzer
from app.agents.software_engineer.intelligence.models import ComplexityReport


class CyclomaticComplexityVisitor(ast.NodeVisitor):
    """AST visitor counting control flow decision points (branches)."""

    def __init__(self) -> None:
        self.complexity = 1

    def visit_If(self, node: ast.If) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_And(self, node: ast.And) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_Or(self, node: ast.Or) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        self.complexity += 1
        self.generic_visit(node)


class CognitiveComplexityVisitor:
    """AST visitor measuring cognitive complexity (nesting penalties and breaks)."""

    def __init__(self) -> None:
        self.complexity = 0

    def calculate(self, node: ast.AST, nesting_level: int = 0) -> int:
        score = 0
        # If, While, For, ExceptHandler increase nesting level
        if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
            score += 1 + nesting_level
            next_nesting = nesting_level + 1
        elif isinstance(node, (ast.BoolOp)):
            score += len(node.values) - 1
            next_nesting = nesting_level
        else:
            next_nesting = nesting_level

        # Traverse children recursively
        for child in ast.iter_child_nodes(node):
            score += self.calculate(child, next_nesting)

        return score


class ASTComplexityAnalyzer(ComplexityAnalyzer):
    """Calculates complexity reports of files analyzing lines of code and AST branches."""

    def calculate_complexity(self, file_path: str, source_code: str) -> ComplexityReport:
        """Parses source code to evaluate maintainability and cyclomatic complexity.

        Args:
            file_path: Relative file path.
            source_code: Content of the source file.

        Returns:
            ComplexityReport model.
        """
        try:
            tree = ast.parse(source_code, filename=file_path)
        except Exception:
            return ComplexityReport(file_path=file_path)

        # 1. Cyclomatic Complexity
        cc_visitor = CyclomaticComplexityVisitor()
        cc_visitor.visit(tree)

        # 2. Cognitive Complexity
        cog_visitor = CognitiveComplexityVisitor()
        cog_score = cog_visitor.calculate(tree)

        # 3. Class and Function counts, and max parameters
        func_count = 0
        class_count = 0
        max_params = 0
        max_func_len = 0
        max_class_len = 0
        func_lens = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_count += 1
                p_count = len(node.args.args) + len(node.args.kwonlyargs)
                if p_count > max_params:
                    max_params = p_count

                # Calculate length of function
                length = (node.end_lineno - node.lineno + 1) if node.end_lineno else 1
                func_lens.append(length)
                if length > max_func_len:
                    max_func_len = length

            elif isinstance(node, ast.ClassDef):
                class_count += 1
                length = (node.end_lineno - node.lineno + 1) if node.end_lineno else 1
                if length > max_class_len:
                    max_class_len = length

        # 4. Nesting Depth
        max_nesting = 0

        def get_nesting(node: ast.AST, current: int) -> int:
            nonlocal max_nesting
            if current > max_nesting:
                max_nesting = current
            nested_types = (ast.If, ast.While, ast.For, ast.Try, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
            next_val = current + 1 if isinstance(node, nested_types) else current
            for child in ast.iter_child_nodes(node):
                get_nesting(child, next_val)
            return max_nesting

        get_nesting(tree, 0)

        total_loc = len(source_code.splitlines())
        avg_func_len = (sum(func_lens) / len(func_lens)) if func_lens else 0.0

        # Calculate a simplified Maintainability Index (MI)
        # Standard MI formula uses volume, CC and LOC
        # MI = 171 - 5.2 * ln(V) - 0.23 * CC - 16.2 * ln(LOC)
        # Here we approximate with a clean fallback mapping:
        cc_penalty = cc_visitor.complexity * 0.5
        loc_penalty = (total_loc / 100) * 2.0
        mi = max(0.0, min(100.0, 100.0 - cc_penalty - loc_penalty))

        return ComplexityReport(
            file_path=file_path,
            cyclomatic_complexity=cc_visitor.complexity,
            cognitive_complexity=cog_score,
            max_nesting_depth=max_nesting,
            function_count=func_count,
            class_count=class_count,
            total_loc=total_loc,
            average_function_length=avg_func_len,
            max_function_length=max_func_len,
            max_class_length=max_class_len,
            max_parameter_count=max_params,
            maintainability_index=round(mi, 2),
        )
