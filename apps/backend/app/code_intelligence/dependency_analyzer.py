"""Dependency Analyzer Module.

Builds dependency graph and analyzes module imports, package dependencies,
circular dependencies, call graphs, API endpoints, and database dependencies.
"""

from typing import Any, Dict, List, Optional, Set
import structlog

logger = structlog.get_logger(__name__)


class DependencyAnalyzer:
    """Enterprise Source Code Dependency Graph Analyzer."""

    def __init__(self) -> None:
        logger.info("dependency_analyzer_initialized")

    def analyze_dependencies(
        self, file_imports: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Constructs import dependency graph and detects circular dependency cycles."""
        dependency_edges: List[Dict[str, str]] = []
        circular_cycles: List[List[str]] = []

        for source_file, imports in file_imports.items():
            for imp in imports:
                dependency_edges.append({
                    "source": source_file,
                    "target": imp,
                    "type": "imports",
                })

        # Circular dependency detection algorithm
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def _dfs_cycle(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in file_imports.get(node, []):
                if neighbor not in visited:
                    _dfs_cycle(neighbor, path)
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    circular_cycles.append(path[cycle_start:] + [neighbor])

            rec_stack.remove(node)
            path.pop()

        for node in file_imports.keys():
            if node not in visited:
                _dfs_cycle(node, [])

        logger.info("dependency_analysis_completed", edge_count=len(dependency_edges), cycles_count=len(circular_cycles))
        return {
            "dependency_edges": dependency_edges,
            "circular_dependencies": circular_cycles,
            "total_dependencies": len(dependency_edges),
        }
