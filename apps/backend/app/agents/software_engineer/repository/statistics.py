"""Computes workspace stats, LOC counts, file counts, and folder aggregates.
"""

import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
from app.agents.software_engineer.repository.models import (
    DirectoryInfo,
    FileInfo,
    RepositoryStatistics,
)

BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".class",
    ".jar",
    ".zip",
    ".tar.gz",
    ".tgz",
    ".rar",
    ".7z",
    ".woff",
    ".woff2",
    ".eot",
    ".ttf",
    ".bin",
    ".pdf",
}

DOCS_EXTENSIONS = {
    ".md",
    ".markdown",
    ".rst",
    ".txt",
    ".docx",
    ".doc",
    ".pdf",
}

CONFIG_EXTENSIONS = {
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".xml",
    ".ini",
    ".conf",
    ".config",
    ".lock",
}

SOURCE_EXTENSIONS = {
    ".py",
    ".pyi",
    ".java",
    ".js",
    ".mjs",
    ".cjs",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".cs",
    ".cpp",
    ".hpp",
    ".cc",
    ".cxx",
    ".h",
    ".kt",
    ".kts",
    ".swift",
    ".php",
    ".html",
    ".htm",
    ".css",
    ".scss",
    ".sql",
    ".sh",
    ".bash",
    ".ps1",
    ".psm1",
    ".psd1",
}


def compute_statistics(
    root_path: str, files: List[FileInfo], max_loc_file_size: int = 1 * 1024 * 1024
) -> RepositoryStatistics:
    """Aggregates metrics and file groupings.

    Args:
        root_path: Workspace absolute path.
        files: List of all scanned files.
        max_loc_file_size: Max size in bytes of files to read for LOC counting.

    Returns:
        Built RepositoryStatistics model.
    """
    total_files = len(files)
    repository_size = sum(f.size for f in files)

    # Classifications
    binary_files = 0
    test_files = 0
    documentation_files = 0
    configuration_files = 0
    source_files = 0

    total_loc = 0
    loc_by_language: Dict[str, int] = {}
    size_by_language: Dict[str, int] = {}

    # List of unique directories
    unique_dirs: Set[str] = set()

    for f in files:
        rel_path = f.relative_path
        abs_path = f.absolute_path
        ext = os.path.splitext(rel_path)[1].lower()

        # Folders parsing
        dirname = os.path.dirname(rel_path)
        while dirname:
            unique_dirs.add(dirname)
            dirname = os.path.dirname(dirname)

        # Classification checks
        is_binary = ext in BINARY_EXTENSIONS
        is_test = False

        # Test pattern: path segments or filename contains 'test' or 'spec'
        path_lower = rel_path.lower()
        fname_lower = os.path.basename(rel_path).lower()
        if (
            "test" in fname_lower
            or "spec" in fname_lower
            or "tests" in path_lower.split(os.sep)
            or "test" in path_lower.split(os.sep)
        ):
            is_test = True

        # Assign file to category
        if is_binary:
            binary_files += 1
        elif is_test:
            test_files += 1
        elif ext in DOCS_EXTENSIONS:
            documentation_files += 1
        elif ext in CONFIG_EXTENSIONS:
            configuration_files += 1
        elif ext in SOURCE_EXTENSIONS or f.language is not None:
            source_files += 1
        else:
            # Fallback
            source_files += 1

        # Calculate LOC for non-binary files
        file_loc = 0
        if not is_binary and f.size <= max_loc_file_size and os.path.exists(abs_path):
            try:
                # Try UTF-8 first, fallback to Latin-1
                try:
                    with open(abs_path, "r", encoding="utf-8") as file_handle:
                        file_loc = sum(1 for _ in file_handle)
                except UnicodeDecodeError:
                    with open(abs_path, "r", encoding="latin-1") as file_handle:
                        file_loc = sum(1 for _ in file_handle)
            except Exception:
                file_loc = 0

        if file_loc > 0:
            total_loc += file_loc
            if f.language:
                loc_by_language[f.language] = loc_by_language.get(f.language, 0) + file_loc

        # Language size aggregation
        if f.language:
            size_by_language[f.language] = size_by_language.get(f.language, 0) + f.size

    # Largest files
    largest_files = sorted(files, key=lambda f: f.size, reverse=True)[:10]

    # Calculate average size
    average_file_size = (repository_size / total_files) if total_files > 0 else 0.0

    # Directory sizes
    dir_sizes: Dict[str, int] = {}
    for f in files:
        dirname = os.path.dirname(f.relative_path)
        # Add to all parent directories
        while dirname:
            dir_sizes[dirname] = dir_sizes.get(dirname, 0) + f.size
            dirname = os.path.dirname(dirname)

    largest_directories: List[DirectoryInfo] = []
    for d_rel, d_size in sorted(dir_sizes.items(), key=lambda item: item[1], reverse=True)[:10]:
        d_abs = os.path.join(root_path, d_rel)
        largest_directories.append(
            DirectoryInfo(
                absolute_path=d_abs,
                relative_path=d_rel,
                size=d_size,
                last_modified=os.path.getmtime(d_abs) if os.path.exists(d_abs) else 0.0,
            )
        )

    # Language percentages (by total size of code files)
    total_code_size = sum(size_by_language.values())
    language_percentages: Dict[str, float] = {}
    if total_code_size > 0:
        for lang, l_size in size_by_language.items():
            language_percentages[lang] = round((l_size / total_code_size) * 100, 2)

    return RepositoryStatistics(
        total_files=total_files,
        total_folders=len(unique_dirs),
        source_files=source_files,
        test_files=test_files,
        documentation_files=documentation_files,
        configuration_files=configuration_files,
        binary_files=binary_files,
        total_loc=total_loc,
        loc_by_language=loc_by_language,
        largest_files=largest_files,
        average_file_size=average_file_size,
        repository_size=repository_size,
        largest_directories=largest_directories,
        language_percentages=language_percentages,
    )
