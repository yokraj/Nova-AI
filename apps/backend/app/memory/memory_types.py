"""Memory Types & Relationship Enums Module.

Defines supported memory classifications and inter-memory relationship types.
"""

from enum import Enum


class MemoryType(str, Enum):
    """Memory entry classification types."""

    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    CONVERSATION = "conversation"
    PROJECT = "project"
    WORKSPACE = "workspace"
    USER_PREFERENCE = "user_preference"
    SEMANTIC = "semantic"
    KNOWLEDGE = "knowledge"
    TEMPORARY = "temporary"
    PINNED = "pinned"
    ARCHIVED = "archived"


class RelationshipType(str, Enum):
    """Relationship linkage types between memory entries."""

    REFERENCES = "references"
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"
    CREATED_FROM = "created_from"
    BELONGS_TO = "belongs_to"
    SUPERSEDES = "supersedes"
    DUPLICATE_OF = "duplicate_of"
