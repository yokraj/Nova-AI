"""Unit and integration tests for the Repository Analyzer module.
"""

import os
import tempfile
import time
import pytest
from pathlib import Path

from app.agents.software_engineer.repository.analyzer import RepositoryAnalyzer
from app.agents.software_engineer.repository.cache import FileSystemRepositoryCache, CacheEntry
from app.agents.software_engineer.repository.detector import ModelRepositoryDetector
from app.agents.software_engineer.repository.models import FileInfo
from app.agents.software_engineer.repository.exceptions import (
    InvalidRepositoryError,
    RepositoryNotFoundError,
    RepositoryScanError,
)
from app.agents.software_engineer.repository.filters import PathFilter
from app.agents.software_engineer.repository.indexer import ModelRepositoryIndexer
from app.agents.software_engineer.repository.scanner import FileSystemRepositoryScanner
from app.agents.software_engineer.repository.statistics import compute_statistics
from app.agents.software_engineer.repository.tree import build_repository_tree
from app.agents.software_engineer.repository.utils import detect_git_info


def test_path_filter_ignore_defaults() -> None:
    """Verifies that PathFilter correctly filters default directories like node_modules and .git."""
    pf = PathFilter()
    assert pf.should_ignore("C:/workspace/.git/config", "C:/workspace") is True
    assert pf.should_ignore("C:/workspace/node_modules/express/package.json", "C:/workspace") is True
    assert pf.should_ignore("C:/workspace/src/main.py", "C:/workspace") is False


def test_path_filter_custom_patterns() -> None:
    """Verifies custom ignore patterns and max file size/depth constraints."""
    pf = PathFilter(ignore_patterns=["*.log", "temp*"], max_file_size=1000, max_depth=3)

    # Custom pattern match
    assert pf.should_ignore("C:/workspace/app.log", "C:/workspace") is True
    assert pf.should_ignore("C:/workspace/temp_dir/file.txt", "C:/workspace") is True

    # Depth match
    assert pf.should_ignore("C:/workspace/src/sub1/sub2/file.py", "C:/workspace") is True
    assert pf.should_ignore("C:/workspace/src/sub1/file.py", "C:/workspace") is False


def test_language_detection() -> None:
    """Verifies language mapping resolver maps extensions correctly."""
    detector = ModelRepositoryDetector()
    assert detector.detect_languages("main.py") == "Python"
    assert detector.detect_languages("index.ts") == "TypeScript"
    assert detector.detect_languages("Cargo.toml") == "JSON" or detector.detect_languages("Cargo.toml") is None
    assert detector.detect_languages("Dockerfile") == "Dockerfile"
    assert detector.detect_languages("script.sh") == "Bash"
    assert detector.detect_languages("unknown.abc") is None


def test_workspace_validation() -> None:
    """Verifies directory check exceptions are raised properly."""
    analyzer = RepositoryAnalyzer()

    # Empty workspace
    with pytest.raises(InvalidRepositoryError):
        analyzer.validate_workspace("")

    # Non-existent workspace
    with pytest.raises(RepositoryNotFoundError):
        analyzer.validate_workspace("C:/non_existent_folder_path_xyz")

    # File path instead of directory
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file_path = tmp_file.name
    try:
        with pytest.raises(InvalidRepositoryError):
            analyzer.validate_workspace(tmp_file_path)
    finally:
        os.remove(tmp_file_path)


def test_git_detection_mock() -> None:
    """Simulates a Git repository structure to test git parser fallbacks."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        git_dir = os.path.join(tmp_dir, ".git")
        os.makedirs(git_dir)

        # Write mock HEAD
        with open(os.path.join(git_dir, "HEAD"), "w", encoding="utf-8") as f:
            f.write("ref: refs/heads/feature/repository-analyzer\n")

        # Write mock config
        with open(os.path.join(git_dir, "config"), "w", encoding="utf-8") as f:
            f.write('[remote "origin"]\n\turl = git@github.com:yokraj/Nova-AI.git\n')

        # Write mock tags
        tags_dir = os.path.join(git_dir, "refs", "tags")
        os.makedirs(tags_dir)
        with open(os.path.join(tags_dir, "v1.0.0"), "w", encoding="utf-8") as f:
            f.write("hash-signature")

        git_info = detect_git_info(tmp_dir)
        assert git_info is not None
        assert git_info.branch == "repository-analyzer"
        assert "origin" in git_info.remotes
        assert git_info.remotes["origin"] == "git@github.com:yokraj/Nova-AI.git"
        assert "v1.0.0" in git_info.tags


def test_manifest_dependency_and_framework_detection() -> None:
    """Verifies that dependency files are parsed correctly and mapped to frameworks."""
    detector = ModelRepositoryDetector()

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create requirements.txt
        req_path = os.path.join(tmp_dir, "requirements.txt")
        with open(req_path, "w", encoding="utf-8") as f:
            f.write("fastapi>=0.110.0\npytest==8.0.0\n")

        # Create package.json
        pkg_path = os.path.join(tmp_dir, "package.json")
        with open(pkg_path, "w", encoding="utf-8") as f:
            f.write('{"dependencies": {"react": "^18.2.0", "next": "14.1.0"}}\n')

        # Create Cargo.toml
        cargo_path = os.path.join(tmp_dir, "Cargo.toml")
        with open(cargo_path, "w", encoding="utf-8") as f:
            f.write('[dependencies]\ntauri = "1.5.0"\n')

        # Create go.mod
        go_path = os.path.join(tmp_dir, "go.mod")
        with open(go_path, "w", encoding="utf-8") as f:
            f.write("module main\n\ngo 1.21\n\nrequire github.com/gin-gonic/gin v1.9.1\n")

        files = ["requirements.txt", "package.json", "Cargo.toml", "go.mod"]
        dependencies = detector.detect_dependencies(tmp_dir, files)

        dep_names = {d.name for d in dependencies}
        assert "fastapi" in dep_names
        assert "react" in dep_names
        assert "next" in dep_names
        assert "tauri" in dep_names
        assert "github.com/gin-gonic/gin" in dep_names

        frameworks = detector.detect_frameworks(tmp_dir, files)
        framework_names = {fw.name for fw in frameworks}
        assert "FastAPI" in framework_names
        assert "React" in framework_names
        assert "Next.js" in framework_names
        assert "Tauri" in framework_names


def test_xml_and_gradle_parsers() -> None:
    """Verifies XML POM, Gradle build, and CSProj NuGet package reference parser."""
    detector = ModelRepositoryDetector()

    with tempfile.TemporaryDirectory() as tmp_dir:
        # pom.xml
        pom_path = os.path.join(tmp_dir, "pom.xml")
        with open(pom_path, "w", encoding="utf-8") as f:
            f.write("""<project>
                <dependencies>
                    <dependency>
                        <groupId>org.springframework.boot</groupId>
                        <artifactId>spring-boot-starter-web</artifactId>
                        <version>3.2.0</version>
                    </dependency>
                </dependencies>
            </project>""")

        # build.gradle
        gradle_path = os.path.join(tmp_dir, "build.gradle")
        with open(gradle_path, "w", encoding="utf-8") as f:
            f.write("dependencies {\n\timplementation 'org.hibernate:hibernate-core:6.4.0.Final'\n}\n")

        # project.csproj
        csproj_path = os.path.join(tmp_dir, "app.csproj")
        with open(csproj_path, "w", encoding="utf-8") as f:
            f.write("""<Project Sdk="Microsoft.NET.Sdk">
                <ItemGroup>
                    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
                </ItemGroup>
            </Project>""")

        files = ["pom.xml", "build.gradle", "app.csproj"]
        dependencies = detector.detect_dependencies(tmp_dir, files)
        dep_names = {d.name for d in dependencies}

        assert "org.springframework.boot:spring-boot-starter-web" in dep_names
        assert "org.hibernate:hibernate-core" in dep_names
        assert "Newtonsoft.Json" in dep_names

        frameworks = detector.detect_frameworks(tmp_dir, files)
        fw_names = {fw.name for fw in frameworks}
        assert "Spring Boot" in fw_names
        assert ".NET" in fw_names


def test_lock_files_parsers() -> None:
    """Verifies that yarn.lock, package-lock.json, poetry.lock are parsed successfully."""
    detector = ModelRepositoryDetector()

    with tempfile.TemporaryDirectory() as tmp_dir:
        # poetry.lock
        poetry_path = os.path.join(tmp_dir, "poetry.lock")
        with open(poetry_path, "w", encoding="utf-8") as f:
            f.write("[[package]]\nname = \"pydantic\"\nversion = \"2.6.1\"\n")

        # package-lock.json
        npm_lock_path = os.path.join(tmp_dir, "package-lock.json")
        with open(npm_lock_path, "w", encoding="utf-8") as f:
            f.write('{"packages": {"node_modules/lodash": {"version": "4.17.21"}}}\n')

        # yarn.lock
        yarn_lock_path = os.path.join(tmp_dir, "yarn.lock")
        with open(yarn_lock_path, "w", encoding="utf-8") as f:
            f.write('"typescript@npm:5.0.0":\n  version "5.0.0"\n')

        files = ["poetry.lock", "package-lock.json", "yarn.lock"]
        dependencies = detector.detect_dependencies(tmp_dir, files)
        dep_names = {d.name for d in dependencies}

        assert "pydantic" in dep_names
        assert "lodash" in dep_names
        assert "typescript" in dep_names


def test_repository_tree_generation() -> None:
    """Verifies tree builder creates hierarchical structures correctly."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Simulate simple folder structure
        os.makedirs(os.path.join(tmp_dir, "src", "core"))
        
        file1 = FileInfo(
            absolute_path=os.path.join(tmp_dir, "main.py"),
            relative_path="main.py",
            size=100,
            last_modified=time.time(),
            language="Python"
        )
        file2 = FileInfo(
            absolute_path=os.path.join(tmp_dir, "src", "core", "utils.py"),
            relative_path="src/core/utils.py",
            size=200,
            last_modified=time.time(),
            language="Python"
        )

        tree = build_repository_tree(tmp_dir, [file1, file2])

        # Assertions
        assert tree.root.node_type == "directory"
        assert tree.root.size == 300
        assert len(tree.root.children) == 2  # main.py and src directory

        src_node = next(child for child in tree.root.children if child.relative_path == "src")
        assert src_node.node_type == "directory"
        assert src_node.size == 200
        assert len(src_node.children) == 1

        core_node = src_node.children[0]
        assert core_node.relative_path == "src/core"
        assert len(core_node.children) == 1
        assert core_node.children[0].relative_path == "src/core/utils.py"
        assert core_node.children[0].node_type == "file"


def test_statistics_and_loc_aggregation() -> None:
    """Tests statistics compiler categorizations and lines of code (LOC) counter."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test scripts
        file1_path = os.path.join(tmp_dir, "main.py")
        with open(file1_path, "w", encoding="utf-8") as f:
            f.write("import sys\n\ndef run():\n\tprint('ok')\n") # 4 lines

        file2_path = os.path.join(tmp_dir, "README.md")
        with open(file2_path, "w", encoding="utf-8") as f:
            f.write("# Project Name\nDocumentation content goes here.\n") # 2 lines

        # Create subfolders and a test file
        tests_dir = os.path.join(tmp_dir, "tests")
        os.makedirs(tests_dir)
        test_path = os.path.join(tests_dir, "test_main.py")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("def test_run():\n\tassert True\n") # 2 lines

        # Assemble FileInfos
        file1 = FileInfo(
            absolute_path=file1_path,
            relative_path="main.py",
            size=len("import sys\n\ndef run():\n\tprint('ok')\n"),
            last_modified=time.time(),
            language="Python"
        )
        file2 = FileInfo(
            absolute_path=file2_path,
            relative_path="README.md",
            size=len("# Project Name\nDocumentation content goes here.\n"),
            last_modified=time.time(),
            language="Markdown"
        )
        file3 = FileInfo(
            absolute_path=test_path,
            relative_path="tests/test_main.py",
            size=len("def test_run():\n\tassert True\n"),
            last_modified=time.time(),
            language="Python"
        )

        stats = compute_statistics(tmp_dir, [file1, file2, file3])

        assert stats.total_files == 3
        assert stats.total_folders == 1
        assert stats.source_files == 1  # main.py
        assert stats.test_files == 1    # tests/test_main.py
        assert stats.documentation_files == 1 # README.md
        assert stats.total_loc == 8
        assert stats.loc_by_language.get("Python") == 6
        assert stats.loc_by_language.get("Markdown") == 2
        assert len(stats.largest_directories) == 1
        assert stats.largest_directories[0].relative_path == "tests"


def test_indexer_lookup_mapping() -> None:
    """Verifies that lookups match indexed keys successfully."""
    indexer = ModelRepositoryIndexer()

    file1 = FileInfo(
        absolute_path="/workspace/src/app.ts",
        relative_path="src/app.ts",
        size=150,
        last_modified=time.time(),
        language="TypeScript",
        framework="React"
    )
    file2 = FileInfo(
        absolute_path="/workspace/src/utils.ts",
        relative_path="src/utils.ts",
        size=100,
        last_modified=time.time(),
        language="TypeScript"
    )

    index = indexer.build_index("/workspace", [file1, file2])

    assert index.by_filename["app.ts"] == ["src/app.ts"]
    assert index.by_extension[".ts"] == ["src/app.ts", "src/utils.ts"]
    assert index.by_directory["src"] == ["src/app.ts", "src/utils.ts"]
    assert index.by_language["TypeScript"] == ["src/app.ts", "src/utils.ts"]
    assert index.by_framework["React"] == ["src/app.ts"]


def test_caching_and_incremental_scanning() -> None:
    """Verifies that caching and incremental scanning skip stats and recalculation."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache_file = os.path.join(tmp_dir, ".nova", "repo_cache.json")
        cache = FileSystemRepositoryCache(cache_file)

        # Register file cache entry
        mtime = time.time()
        entry = CacheEntry(mtime=mtime, size=150, sha256="abc123hash", language="Python", framework=None)
        cache.set_entry("main.py", entry)
        cache.save()

        # Reload cache to test deserialization
        new_cache = FileSystemRepositoryCache(cache_file)
        cached_val = new_cache.get_entry("main.py")
        assert cached_val is not None
        assert cached_val.sha256 == "abc123hash"
        assert cached_val.size == 150

        # Simulate scanning with cache
        file_path = os.path.join(tmp_dir, "main.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("print('hello cached scan')")
            
        # Match mtime and size exactly
        os.utime(file_path, (mtime, mtime))
        # Ensure size matches
        stat_info = os.stat(file_path)
        cache.set_entry("main.py", CacheEntry(mtime=mtime, size=stat_info.st_size, sha256="hashed", language="Python"))
        cache.save()

        scanner = FileSystemRepositoryScanner()
        files = scanner.scan(tmp_dir, cache)

        assert len(files) == 1
        assert files[0].relative_path == "main.py"
        assert files[0].sha256 == "hashed"
        assert files[0].language == "Python"


def test_complete_analyzer_run() -> None:
    """Verifies end-to-end RepositoryAnalyzer orchestrations and legacy APIs."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test layout
        src_dir = os.path.join(tmp_dir, "src")
        os.makedirs(src_dir)

        main_py = os.path.join(src_dir, "main.py")
        with open(main_py, "w", encoding="utf-8") as f:
            f.write("def start():\n\tpass\n")

        requirements = os.path.join(tmp_dir, "requirements.txt")
        with open(requirements, "w", encoding="utf-8") as f:
            f.write("fastapi>=0.110.0\n")

        # Mock Git
        git_dir = os.path.join(tmp_dir, ".git")
        os.makedirs(git_dir)
        with open(os.path.join(git_dir, "HEAD"), "w", encoding="utf-8") as f:
            f.write("ref: refs/heads/main\n")

        analyzer = RepositoryAnalyzer(workspace_root=tmp_dir)
        result = analyzer.analyze(tmp_dir)

        # Assert full scan result compilation
        assert result.scan_duration > 0
        assert result.repository_info.root_path == os.path.abspath(tmp_dir)
        assert result.repository_info.statistics.total_files == 2
        assert "Python" in result.index.by_language
        assert "FastAPI" in [fw.name for fw in result.repository_info.metadata.frameworks]

        # Verify legacy APIs
        branches = analyzer.analyze_branches()
        assert "main" in branches

        commits = analyzer.get_commit_history()
        assert isinstance(commits, list)
