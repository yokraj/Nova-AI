"""Nova AI Enterprise Memory & Knowledge Foundation Package.

Exports core memory models, repositories, managers, search, scoring, compression, cleanup,
statistics, services, and the master MemoryEngine.
"""

from app.memory.config import MemoryConfig
from app.memory.exceptions import (
    MemoryError,
    MemoryNotFoundError,
    MemoryValidationError,
    MemoryRelationshipError,
    MemoryStorageError,
    MemoryCompressionError,
    MemoryAccessDeniedError,
)
from app.memory.memory_types import MemoryType, RelationshipType
from app.memory.models import (
    MemoryEntryModel,
    MemoryChunkModel,
    MemoryTagModel,
    MemoryRelationshipModel,
    WorkspaceMemoryModel,
    ProjectMemoryModel,
    ConversationMemoryModel,
    UserPreferenceModel,
    MemoryStatisticsModel,
)
from app.memory.schemas import (
    MemoryEntryCreate,
    MemoryEntryUpdate,
    MemoryRelationshipCreate,
    MemoryEntryResponse,
    MemorySearchQuery,
    WorkspaceMemorySchema,
    ProjectMemorySchema,
    UserPreferenceSchema,
    MemoryStatisticsSchema,
)
from app.memory.repository import MemoryRepository
from app.memory.memory_store import MemoryStore
from app.memory.memory_scoring import MemoryScoringEngine
from app.memory.memory_compression import MemoryCompressor
from app.memory.memory_cleanup import MemoryCleaner
from app.memory.memory_search import MemorySearch
from app.memory.memory_indexer import MemoryIndexer
from app.memory.conversation_memory import ConversationMemoryManager
from app.memory.workspace_memory import WorkspaceMemoryManager
from app.memory.project_memory import ProjectMemoryManager
from app.memory.user_memory import UserMemoryManager
from app.memory.semantic_memory import SemanticMemoryManager
from app.memory.memory_manager import MemoryManager
from app.memory.statistics import MemoryStatisticsTracker
from app.memory.service import (
    MemoryService,
    ConversationMemoryService,
    WorkspaceMemoryService,
    ProjectMemoryService,
    UserMemoryService,
)
from app.memory.engine import MemoryEngine

__all__ = [
    "MemoryConfig",
    "MemoryError",
    "MemoryNotFoundError",
    "MemoryValidationError",
    "MemoryRelationshipError",
    "MemoryStorageError",
    "MemoryCompressionError",
    "MemoryAccessDeniedError",
    "MemoryType",
    "RelationshipType",
    "MemoryEntryModel",
    "MemoryChunkModel",
    "MemoryTagModel",
    "MemoryRelationshipModel",
    "WorkspaceMemoryModel",
    "ProjectMemoryModel",
    "ConversationMemoryModel",
    "UserPreferenceModel",
    "MemoryStatisticsModel",
    "MemoryEntryCreate",
    "MemoryEntryUpdate",
    "MemoryRelationshipCreate",
    "MemoryEntryResponse",
    "MemorySearchQuery",
    "WorkspaceMemorySchema",
    "ProjectMemorySchema",
    "UserPreferenceSchema",
    "MemoryStatisticsSchema",
    "MemoryRepository",
    "MemoryStore",
    "MemoryScoringEngine",
    "MemoryCompressor",
    "MemoryCleaner",
    "MemorySearch",
    "MemoryIndexer",
    "ConversationMemoryManager",
    "WorkspaceMemoryManager",
    "ProjectMemoryManager",
    "UserMemoryManager",
    "SemanticMemoryManager",
    "MemoryManager",
    "MemoryStatisticsTracker",
    "MemoryService",
    "ConversationMemoryService",
    "WorkspaceMemoryService",
    "ProjectMemoryService",
    "UserMemoryService",
    "MemoryEngine",
]
