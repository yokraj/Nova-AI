"""Context Builder formats retrieved results into structural context packages.
"""

from typing import List
from app.ai.memory.models import RetrievalResult, ContextPackage, MemoryType

class ContextBuilder:
    """Assembles segmented contexts for prompt insertions."""

    def build_context_package(self, results: List[RetrievalResult]) -> ContextPackage:
        """Organizes list of RetrievalResults by memory type categories."""
        sys_parts = []
        conv_parts = []
        proj_parts = []
        code_parts = []

        for res in results:
            m_type_str = res.metadata.get("memory_type")
            
            # Segment content
            content_line = f"- {res.content}"
            if m_type_str == MemoryType.CONVERSATION.value:
                conv_parts.append(content_line)
            elif m_type_str == MemoryType.PROJECT.value:
                proj_parts.append(content_line)
            elif m_type_str == MemoryType.CODE.value:
                code_parts.append(content_line)
            else:
                sys_parts.append(content_line)

        return ContextPackage(
            system_context="\n".join(sys_parts),
            memory_context="\n".join(conv_parts),
            project_context="\n".join(proj_parts),
            code_context="\n".join(code_parts)
        )
