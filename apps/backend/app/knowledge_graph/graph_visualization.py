"""Graph Visualization Module.

Generates Mermaid diagram markup (graph TD), JSON graph export, Node-link format,
Tree views, and Dependency graphs for interactive visualization.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.knowledge_graph.schemas import GraphVisualizationResponse

logger = structlog.get_logger(__name__)


class GraphVisualizer:
    """Enterprise Knowledge Graph Renderer & Visualizer."""

    def __init__(self) -> None:
        logger.info("graph_visualizer_initialized")

    def render_mermaid(
        self, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]]
    ) -> str:
        """Renders GitHub-compatible Mermaid graph TD markup."""
        lines = ["graph TD"]
        sanitized: Dict[str, str] = {}

        for idx, ent in enumerate(entities, 1):
            node_key = f"N{idx}"
            sanitized[ent.get("id", ent["name"])] = node_key
            label = f"{ent['name']} ({ent.get('entity_type', 'Node')})"
            lines.append(f'  {node_key}["{label}"]')

        for rel in relationships:
            src_key = sanitized.get(rel.get("source_id", rel.get("source_name")))
            tgt_key = sanitized.get(rel.get("target_id", rel.get("target_name")))
            rel_label = rel.get("relationship_type", "related_to")
            if src_key and tgt_key:
                lines.append(f"  {src_key} -- {rel_label} --> {tgt_key}")

        mermaid_code = "\n".join(lines)
        logger.info("mermaid_graph_rendered", line_count=len(lines))
        return mermaid_code

    def export_graph_visualization(
        self, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]]
    ) -> GraphVisualizationResponse:
        """Generates comprehensive graph export package in JSON and Mermaid formats."""
        mermaid_markup = self.render_mermaid(entities, relationships)
        json_graph = {
            "nodes": entities,
            "links": relationships,
        }

        return GraphVisualizationResponse(
            mermaid_code=mermaid_markup,
            json_graph=json_graph,
            node_count=len(entities),
            edge_count=len(relationships),
        )
