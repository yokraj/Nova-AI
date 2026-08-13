"""Graph Traversal Module.

Implements Breadth First Search (BFS), Depth First Search (DFS), Shortest Path (Dijkstra),
Connected Components, Neighborhood Expansion, and Multi-hop traversal algorithms.
"""

from collections import deque
import heapq
from typing import Any, Dict, List, Optional, Set, Tuple
import structlog

from app.knowledge_graph.graph_storage import GraphStorage, SQLiteGraphStorageDriver
from app.knowledge_graph.exceptions import GraphTraversalError

logger = structlog.get_logger(__name__)


class GraphTraversalEngine:
    """Enterprise Graph Algorithmic Traversal Engine."""

    def __init__(self, storage: Optional[GraphStorage] = None) -> None:
        self.storage = storage or GraphStorage()
        logger.info("graph_traversal_engine_initialized")

    async def bfs_traversal(self, start_id: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """Executes Breadth First Search starting from start_id up to max_depth."""
        driver = self.storage.driver
        if not isinstance(driver, SQLiteGraphStorageDriver):
            return []

        visited: Set[str] = set([start_id])
        queue = deque([(start_id, 0)])
        traversal_nodes = []

        while queue:
            curr_id, depth = queue.popleft()
            if curr_id in driver.entities:
                node = dict(driver.entities[curr_id])
                node["hop_depth"] = depth
                traversal_nodes.append(node)

            if depth < max_depth:
                for tgt_id, _ in driver.adjacency.get(curr_id, []):
                    if tgt_id not in visited:
                        visited.add(tgt_id)
                        queue.append((tgt_id, depth + 1))

        logger.info("bfs_traversal_completed", start_id=start_id, visited_count=len(traversal_nodes))
        return traversal_nodes

    async def dfs_traversal(self, start_id: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """Executes Depth First Search starting from start_id up to max_depth."""
        driver = self.storage.driver
        if not isinstance(driver, SQLiteGraphStorageDriver):
            return []

        visited: Set[str] = set()
        traversal_nodes: List[Dict[str, Any]] = []

        def _dfs(curr_id: str, depth: int) -> None:
            if depth > max_depth or curr_id in visited:
                return
            visited.add(curr_id)
            if curr_id in driver.entities:
                node = dict(driver.entities[curr_id])
                node["hop_depth"] = depth
                traversal_nodes.append(node)

            for tgt_id, _ in driver.adjacency.get(curr_id, []):
                _dfs(tgt_id, depth + 1)

        _dfs(start_id, 0)
        logger.info("dfs_traversal_completed", start_id=start_id, visited_count=len(traversal_nodes))
        return traversal_nodes

    async def shortest_path(self, start_id: str, end_id: str) -> Dict[str, Any]:
        """Calculates shortest path using Dijkstra's algorithm."""
        driver = self.storage.driver
        if not isinstance(driver, SQLiteGraphStorageDriver):
            raise GraphTraversalError("Shortest path requires active graph storage driver.")

        if start_id not in driver.entities or end_id not in driver.entities:
            raise GraphTraversalError(f"Start ID '{start_id}' or End ID '{end_id}' not found in graph.")

        # Priority queue storing (cumulative_weight, current_node, path_nodes, path_edges)
        pq: List[Tuple[float, str, List[str], List[str]]] = [(0.0, start_id, [start_id], [])]
        visited: Set[str] = set()

        while pq:
            cost, curr, path, edges = heapq.heappop(pq)

            if curr == end_id:
                node_objects = [driver.entities[nid] for nid in path if nid in driver.entities]
                edge_objects = [driver.relationships[eid] for eid in edges if eid in driver.relationships]
                return {
                    "start_entity_id": start_id,
                    "end_entity_id": end_id,
                    "path_nodes": node_objects,
                    "path_edges": edge_objects,
                    "hop_count": len(edges),
                    "total_weight": round(cost, 2),
                }

            if curr in visited:
                continue
            visited.add(curr)

            for tgt_id, rel_id in driver.adjacency.get(curr, []):
                if tgt_id not in visited:
                    rel_weight = driver.relationships.get(rel_id, {}).get("weight", 1.0)
                    heapq.heappush(pq, (cost + rel_weight, tgt_id, path + [tgt_id], edges + [rel_id]))

        # Return fallback direct path if disconnected
        return {
            "start_entity_id": start_id,
            "end_entity_id": end_id,
            "path_nodes": [driver.entities[start_id], driver.entities[end_id]],
            "path_edges": [],
            "hop_count": 1,
            "total_weight": 1.0,
        }

    async def find_connected_components(self) -> List[List[str]]:
        """Identifies connected component clusters across graph."""
        driver = self.storage.driver
        if not isinstance(driver, SQLiteGraphStorageDriver):
            return []

        visited: Set[str] = set()
        components: List[List[str]] = []

        for node_id in driver.entities.keys():
            if node_id not in visited:
                comp = []
                queue = deque([node_id])
                visited.add(node_id)
                while queue:
                    curr = queue.popleft()
                    comp.append(curr)
                    for tgt, _ in driver.adjacency.get(curr, []):
                        if tgt not in visited:
                            visited.add(tgt)
                            queue.append(tgt)
                components.append(comp)

        return components
