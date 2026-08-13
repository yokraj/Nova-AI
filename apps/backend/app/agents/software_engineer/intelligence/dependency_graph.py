"""Builds and analyzes dependency graphs of imports between project modules.
"""

from typing import Any, Dict, List, Set

from app.agents.software_engineer.intelligence.interfaces import DependencyAnalyzer
from app.agents.software_engineer.intelligence.models import (
    DependencyGraph,
    DependencyNode,
    ImportInfo,
)


class ModuleDependencyAnalyzer(DependencyAnalyzer):
    """Calculates dependencies, dependents mappings, and circular import chains."""

    def analyze_dependencies(
        self, workspace_path: str, file_imports: Dict[str, List[ImportInfo]]
    ) -> DependencyGraph:
        """Constructs module dependency graph.

        Args:
            workspace_path: Workspace root path.
            file_imports: Mapping of relative file path to list of imports occurring in it.

        Returns:
            DependencyGraph model.
        """
        from app.agents.software_engineer.intelligence.import_resolver import ImportResolver

        resolver = ImportResolver(workspace_path)
        nodes: Dict[str, DependencyNode] = {}
        dependencies: Dict[str, List[str]] = {}
        dependents: Dict[str, List[str]] = {}

        # 1. Resolve all imports and map to modules
        for f_path, imports_list in file_imports.items():
            current_mod = resolver.get_module_name(f_path)

            if current_mod not in nodes:
                nodes[current_mod] = DependencyNode(module_name=current_mod, file_path=f_path)

            nodes[current_mod].imports.extend(imports_list)
            dependencies[current_mod] = []

            for imp in imports_list:
                resolved_rel = resolver.resolve_import(imp.module_name, os.path.join(workspace_path, f_path), imp.level)
                if resolved_rel:
                    imported_mod = resolver.get_module_name(resolved_rel)
                    if imported_mod != current_mod and imported_mod not in dependencies[current_mod]:
                        dependencies[current_mod].append(imported_mod)

        # 2. Build reverse dependents map
        for src, dests in dependencies.items():
            for d in dests:
                dependents.setdefault(d, []).append(src)

        # 3. Detect circular dependencies using DFS cycle detection
        circular = self._detect_circular_dependencies(dependencies)

        return DependencyGraph(
            nodes=nodes,
            dependencies=dependencies,
            dependents=dependents,
            circular_dependencies=circular,
        )

    def _detect_circular_dependencies(self, dependencies: Dict[str, List[str]]) -> List[List[str]]:
        """DFS traversal to find cycles in the import graph."""
        visited: Set[str] = set()
        stack: List[str] = []
        cycles: List[List[str]] = []

        def dfs(node: str) -> None:
            if node in stack:
                # Cycle found! Extract the cycle path.
                idx = stack.index(node)
                cycle = stack[idx:] + [node]
                # Normalize cycle representation so duplicates (e.g. A->B->A and B->A->B) are avoided
                # Standard sorting shift
                min_idx = cycle.index(min(cycle[:-1]))
                normalized_cycle = cycle[min_idx:-1] + cycle[:min_idx] + [cycle[min_idx]]
                if normalized_cycle not in cycles:
                    cycles.append(normalized_cycle)
                return

            if node in visited:
                return

            stack.append(node)
            for neighbor in dependencies.get(node, []):
                dfs(neighbor)
            stack.pop()
            visited.add(node)

        for n in dependencies:
            dfs(n)

        return cycles


import os
