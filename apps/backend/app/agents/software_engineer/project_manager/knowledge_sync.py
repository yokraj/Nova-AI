"""Knowledge Sync manages storing project decisions and completed tasks to the knowledge base.
"""

from typing import List
from app.agents.software_engineer.project_manager.interfaces import IKnowledgeManager
from app.agents.software_engineer.project_manager.models import Project
from app.agents.software_engineer.documentation.knowledge_builder import LocalKnowledgeBuilder
from app.agents.software_engineer.documentation.knowledge_index import LocalKnowledgeIndexer
from app.agents.software_engineer.documentation.models import KnowledgeEntry

class LocalKnowledgeSync(IKnowledgeManager):
    """Synchronizes project decisions and completed tasks with the documentation Knowledge Base."""

    def __init__(self) -> None:
        self.builder = LocalKnowledgeBuilder()
        self.indexer = LocalKnowledgeIndexer()

    def sync_knowledge(self, project: Project) -> bool:
        """Collects completed tasks and architectural choices to index as knowledge."""
        entries: List[KnowledgeEntry] = []
        
        # 1. Store project decisions and architecture choices
        for constraint in project.requirements.constraints:
            entries.append(KnowledgeEntry(
                title=f"Project Constraint - {project.name}",
                content=f"Constraint: {constraint}",
                category="constraint",
                timestamp=0.0,
            ))

        # 2. Add completed tasks
        for epic in project.epics:
            for feature in epic.features:
                for task in feature.tasks:
                    if task.status == "COMPLETED":
                        entries.append(KnowledgeEntry(
                            title=f"Completed Task - {task.title}",
                            content=f"Task: {task.description} completed under Epic {epic.name}.",
                            category="tasks",
                            timestamp=0.0,
                        ))

        # Perform index mock operations
        try:
            self.indexer.index_knowledge(entries)
            return True
        except Exception:
            return False
