"""Detects code duplication by comparing canonicalized AST subtree structures.
"""

import ast
import hashlib
from typing import Any, Dict, List, Tuple

from app.agents.software_engineer.intelligence.interfaces import DuplicateAnalyzer
from app.agents.software_engineer.intelligence.models import DuplicateReport


class ASTCanonicalizer(ast.NodeTransformer):
    """AST Transformer rewriting variable names and constants to placeholders."""

    def visit_Name(self, node: ast.Name) -> ast.Name:
        # Standardize all identifiers to 'VAR'
        return ast.Name(id="VAR", ctx=node.ctx)

    def visit_Constant(self, node: ast.Constant) -> ast.Constant:
        # Standardize all constants to 'CONST'
        return ast.Constant(value="CONST")

    def visit_arg(self, node: ast.arg) -> ast.arg:
        # Standardize parameter names
        return ast.arg(arg="PARAM", annotation=None)


class ASTDuplicateDetector(DuplicateAnalyzer):
    """Compares Python AST subtrees to locate duplicated functions and classes."""

    def find_duplicates(self, ast_trees: Dict[str, Any]) -> List[DuplicateReport]:
        """Scans parsed ASTs to find duplicate declarations.

        Args:
            ast_trees: Mapping of relative path to parsed raw AST.

        Returns:
            List of DuplicateReport instances.
        """
        duplicates: List[DuplicateReport] = []
        # Maps shape hash to list of (file_path, node, source_snippet)
        shapes: Dict[str, List[Tuple[str, Any, str]]] = {}

        transformer = ASTCanonicalizer()

        for file_path, raw_ast in ast_trees.items():
            if not raw_ast:
                continue

            # Traverse the AST to find all functions and classes
            for node in ast.walk(raw_ast):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    # Ignore very small bodies to avoid trivial duplicates (e.g. pass, or simple returns)
                    length = (node.end_lineno - node.lineno + 1) if node.end_lineno else 1
                    if length < 5:
                        continue

                    # Generate canonical code dump
                    try:
                        # Deep copy node by parsing its unparsed source to avoid modifying original AST
                        source_snippet = ast.unparse(node)
                        node_copy = ast.parse(source_snippet).body[0]

                        # Apply transformation
                        canonical_node = transformer.visit(node_copy)
                        canonical_dump = ast.dump(canonical_node)

                        # Hash the canonical structure
                        shape_hash = hashlib.sha256(canonical_dump.encode("utf-8")).hexdigest()
                        shapes.setdefault(shape_hash, []).append((file_path, node, source_snippet))
                    except Exception:
                        continue

        # 2. Extract duplicates
        for shape_hash, instances in shapes.items():
            if len(instances) > 1:
                # Compare each pair of duplicate instances
                for i in range(len(instances)):
                    for j in range(i + 1, len(instances)):
                        file_a, node_a, snippet_a = instances[i]
                        file_b, node_b, snippet_b = instances[j]

                        # Avoid matching identical lines in the same file (self-overlap)
                        if file_a == file_b and node_a.lineno == node_b.lineno:
                            continue

                        duplicates.append(
                            DuplicateReport(
                                file_path_a=file_a,
                                file_path_b=file_b,
                                line_start_a=node_a.lineno,
                                line_start_b=node_b.lineno,
                                line_end_a=node_a.end_lineno or node_a.lineno,
                                line_end_b=node_b.end_lineno or node_b.lineno,
                                similarity_score=1.0,
                                code_snippet=snippet_a[:200] + "\n..." if len(snippet_a) > 200 else snippet_a,
                            )
                        )

        return duplicates
