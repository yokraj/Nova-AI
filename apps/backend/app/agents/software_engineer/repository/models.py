"""Pydantic models representing repository structures and metadata.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    """Details about a single file in the repository."""

    absolute_path: str = Field(..., description="Absolute file path on the system.")
    relative_path: str = Field(..., description="Relative path from workspace root.")
    size: int = Field(..., description="Size of file in bytes.")
    last_modified: float = Field(..., description="Modification epoch timestamp.")
    sha256: Optional[str] = Field(None, description="SHA256 checksum of the file contents.")
    language: Optional[str] = Field(None, description="Detected language name.")
    framework: Optional[str] = Field(None, description="Detected framework associated with the file.")


class DirectoryInfo(BaseModel):
    """Details about a directory in the repository."""

    absolute_path: str = Field(..., description="Absolute directory path.")
    relative_path: str = Field(..., description="Relative path from workspace root.")
    size: int = Field(..., description="Total size of all recursive files in bytes.")
    last_modified: float = Field(..., description="Modification epoch timestamp.")


class LanguageInfo(BaseModel):
    """Details about a language detected in the repository."""

    name: str = Field(..., description="Name of the language.")
    extension: str = Field(..., description="Primary file extension.")
    lines_of_code: int = Field(0, description="Total lines of code detected in this language.")


class FrameworkInfo(BaseModel):
    """Details about a framework detected in the repository."""

    name: str = Field(..., description="Name of the framework.")
    version: Optional[str] = Field(None, description="Detected framework version.")


class DependencyInfo(BaseModel):
    """Details about a dependency defined in project manifests."""

    name: str = Field(..., description="Name of the library or package.")
    version: Optional[str] = Field(None, description="Declared version constraint or lock version.")
    manager: str = Field(..., description="Dependency manager used (e.g. npm, pip, cargo).")


class GitInfo(BaseModel):
    """Git repository metadata."""

    repository_root: str = Field(..., description="Path to the git repository root directory.")
    branch: Optional[str] = Field(None, description="Active branch name.")
    remotes: Dict[str, str] = Field(default_factory=dict, description="Configured git remote URLs.")
    tags: List[str] = Field(default_factory=list, description="Git tags list.")
    is_clean: bool = Field(True, description="True if no modified/untracked files exist.")
    repository_size: int = Field(0, description="Estimated total repository size in bytes.")
    commit_count: Optional[int] = Field(None, description="Total local commit count.")


class RepositoryNode(BaseModel):
    """Hierarchical node inside a RepositoryTree."""

    absolute_path: str = Field(..., description="Absolute path on system.")
    relative_path: str = Field(..., description="Relative path from workspace root.")
    depth: int = Field(..., description="Directory nesting depth starting from 0.")
    node_type: str = Field(..., description="Type of node: 'file' or 'directory'.")
    size: int = Field(..., description="Size in bytes.")
    last_modified: float = Field(..., description="Modification timestamp.")
    language: Optional[str] = Field(None, description="Associated language if file.")
    framework: Optional[str] = Field(None, description="Associated framework.")
    parent: Optional["RepositoryNode"] = Field(
        default=None, exclude=True, repr=False, description="Parent node reference."
    )
    children: List["RepositoryNode"] = Field(default_factory=list, description="Child nodes list.")


class RepositoryTree(BaseModel):
    """Hierarchical tree representing the repository file structure."""

    root: RepositoryNode = Field(..., description="Root directory node of the repository.")


class RepositoryStatistics(BaseModel):
    """Consolidated metrics and statistics about the repository."""

    total_files: int = Field(0, description="Total number of scanned files.")
    total_folders: int = Field(0, description="Total number of scanned directories.")
    source_files: int = Field(0, description="Number of source code files.")
    test_files: int = Field(0, description="Number of unit/integration test files.")
    documentation_files: int = Field(0, description="Number of documentation files.")
    configuration_files: int = Field(0, description="Number of configuration files.")
    binary_files: int = Field(0, description="Number of binary files.")
    total_loc: int = Field(0, description="Total lines of code.")
    loc_by_language: Dict[str, int] = Field(default_factory=dict, description="LOC count per language.")
    largest_files: List[FileInfo] = Field(default_factory=list, description="Top largest files.")
    average_file_size: float = Field(0.0, description="Average file size in bytes.")
    repository_size: int = Field(0, description="Total repository size in bytes.")
    largest_directories: List[DirectoryInfo] = Field(default_factory=list, description="Top largest directories.")
    language_percentages: Dict[str, float] = Field(
        default_factory=dict, description="File size percentage per language."
    )


class RepositoryIndex(BaseModel):
    """In-memory indexes for fast lookup and search operations."""

    by_filename: Dict[str, List[str]] = Field(default_factory=dict)
    by_extension: Dict[str, List[str]] = Field(default_factory=dict)
    by_directory: Dict[str, List[str]] = Field(default_factory=dict)
    by_language: Dict[str, List[str]] = Field(default_factory=dict)
    by_framework: Dict[str, List[str]] = Field(default_factory=dict)
    by_dependency: Dict[str, List[str]] = Field(default_factory=dict)
    by_relative_path: Dict[str, str] = Field(default_factory=dict)
    by_absolute_path: Dict[str, str] = Field(default_factory=dict)


class RepositoryMetadata(BaseModel):
    """Aggregated metadata containing languages, frameworks, dependencies and git state."""

    languages: List[LanguageInfo] = Field(default_factory=list)
    frameworks: List[FrameworkInfo] = Field(default_factory=list)
    dependencies: List[DependencyInfo] = Field(default_factory=list)
    git_info: Optional[GitInfo] = Field(None)


class RepositoryInfo(BaseModel):
    """Aggregated information summary of the repository."""

    root_path: str = Field(..., description="Root path of the repository.")
    metadata: RepositoryMetadata = Field(..., description="Repository metadata summary.")
    statistics: RepositoryStatistics = Field(..., description="Repository statistics summary.")


class ScanResult(BaseModel):
    """Result payload of a repository scan/analysis run."""

    repository_info: RepositoryInfo = Field(..., description="Metadata and statistics report.")
    tree: RepositoryTree = Field(..., description="Hierarchical file structure tree.")
    index: RepositoryIndex = Field(..., description="Built indexes mapping names, extensions, and types.")
    scan_duration: float = Field(..., description="Total time taken to analyze workspace in seconds.")
    scan_timestamp: float = Field(..., description="Epoch timestamp when scan completed.")


# Resolve circular reference within RepositoryNode parent/children fields
RepositoryNode.model_rebuild()
