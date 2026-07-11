"""SoftwareCapability enum listing agent capabilities tags.
"""

from enum import Enum


class SoftwareCapability(str, Enum):
    """Enumeration of capabilities supported by the Software Engineering Agent."""

    READ_CODE = "ReadCode"
    WRITE_CODE = "WriteCode"
    REFACTOR_CODE = "RefactorCode"
    GENERATE_TESTS = "GenerateTests"
    GENERATE_DOCUMENTATION = "GenerateDocumentation"
    REVIEW_CODE = "ReviewCode"
    ANALYZE_ARCHITECTURE = "AnalyzeArchitecture"
    SEARCH_REPOSITORY = "SearchRepository"
    EXPLAIN_CODE = "ExplainCode"
    DEBUG = "Debug"
    WORKSPACE_MANAGEMENT = "WorkspaceManagement"
