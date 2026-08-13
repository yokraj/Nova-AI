"""Orchestrates language, framework, dependency, and Git metadata aggregation.
"""

from typing import List, Optional

from app.agents.software_engineer.repository.interfaces import RepositoryDetector
from app.agents.software_engineer.repository.models import (
    FileInfo,
    LanguageInfo,
    RepositoryMetadata,
    RepositoryStatistics,
)
from app.agents.software_engineer.repository.utils import detect_git_info


def generate_metadata(
    workspace_path: str,
    files: List[FileInfo],
    stats: RepositoryStatistics,
    detector: RepositoryDetector,
) -> RepositoryMetadata:
    """Consolidates repository intelligence metadata.

    Args:
        workspace_path: Workspace root directory path.
        files: List of all scanned files.
        stats: Computed repository statistics.
        detector: Active RepositoryDetector instance.

    Returns:
        Built RepositoryMetadata model.
    """
    # 1. Languages Metadata
    language_infos: List[LanguageInfo] = []
    # Identify primary extension for each language
    lang_extensions = {}
    for f in files:
        if f.language:
            ext = f.relative_path.split(".")[-1]
            if ext:
                lang_extensions[f.language] = f".{ext}"

    for lang, loc in stats.loc_by_language.items():
        primary_ext = lang_extensions.get(lang, "")
        language_infos.append(LanguageInfo(name=lang, extension=primary_ext, lines_of_code=loc))

    # For languages that had 0 LOC (e.g. only empty files or binary?), make sure they are listed if they exist in files
    seen_langs = {info.name for info in language_infos}
    for f in files:
        if f.language and f.language not in seen_langs:
            seen_langs.add(f.language)
            primary_ext = lang_extensions.get(f.language, "")
            language_infos.append(LanguageInfo(name=f.language, extension=primary_ext, lines_of_code=0))

    # 2. Frameworks
    rel_files = [f.relative_path for f in files]
    frameworks = detector.detect_frameworks(workspace_path, rel_files)

    # 3. Dependencies
    dependencies = detector.detect_dependencies(workspace_path, rel_files)

    # 4. GitInfo
    git_info = detect_git_info(workspace_path)

    return RepositoryMetadata(
        languages=language_infos,
        frameworks=frameworks,
        dependencies=dependencies,
        git_info=git_info,
    )
