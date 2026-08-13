"""Implements programming language, framework, and manifest dependency detection.
"""

import json
import os
import re
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.agents.software_engineer.repository.interfaces import RepositoryDetector
from app.agents.software_engineer.repository.models import DependencyInfo, FrameworkInfo

LANGUAGE_MAP = {
    ".py": "Python",
    ".pyi": "Python",
    ".java": "Java",
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".cs": "C#",
    ".cpp": "C++",
    ".hpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".h": "C++",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".swift": "Swift",
    ".php": "PHP",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sql": "SQL",
    ".md": "Markdown",
    ".markdown": "Markdown",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".xml": "XML",
    ".sh": "Bash",
    ".bash": "Bash",
    ".ps1": "PowerShell",
    ".psm1": "PowerShell",
    ".psd1": "PowerShell",
}


class ModelRepositoryDetector(RepositoryDetector):
    """Detects software languages, libraries, and frameworks."""

    def detect_languages(self, file_path: Union[str, Path]) -> Optional[str]:
        """Resolves file path to language identifier.

        Args:
            file_path: The file to identify.

        Returns:
            Name of the language (e.g. 'Python') or None if undetected.
        """
        p = Path(file_path)
        if p.name.lower().startswith("dockerfile"):
            return "Dockerfile"
        ext = p.suffix.lower()
        return LANGUAGE_MAP.get(ext)

    def detect_frameworks(self, workspace_path: str, files: List[str]) -> List[FrameworkInfo]:
        """Detects framework profiles from workspace file listings and dependencies.

        Args:
            workspace_path: Root workspace path.
            files: Relative paths of all files in workspace.

        Returns:
            List of detected FrameworkInfo models.
        """
        frameworks = []
        # Parse all manifests to fetch dependencies
        dependencies = self.detect_dependencies(workspace_path, files)
        dep_names = {d.name.lower() for d in dependencies}

        # Check Python frameworks
        if "fastapi" in dep_names:
            frameworks.append(FrameworkInfo(name="FastAPI"))
        if "flask" in dep_names:
            frameworks.append(FrameworkInfo(name="Flask"))
        if "django" in dep_names:
            frameworks.append(FrameworkInfo(name="Django"))

        # Check JS/TS frameworks
        if "react" in dep_names:
            frameworks.append(FrameworkInfo(name="React"))
        if "next" in dep_names:
            frameworks.append(FrameworkInfo(name="Next.js"))
        if "vue" in dep_names:
            frameworks.append(FrameworkInfo(name="Vue"))
        if "@angular/core" in dep_names:
            frameworks.append(FrameworkInfo(name="Angular"))
        if "express" in dep_names:
            frameworks.append(FrameworkInfo(name="Express"))
        if "electron" in dep_names:
            frameworks.append(FrameworkInfo(name="Electron"))
        if "@tauri-apps/api" in dep_names or "tauri" in dep_names:
            frameworks.append(FrameworkInfo(name="Tauri"))
        if "react-native" in dep_names:
            frameworks.append(FrameworkInfo(name="React Native"))

        # Check JVM/Java frameworks
        has_springboot = any("spring-boot" in name for name in dep_names)
        if has_springboot:
            frameworks.append(FrameworkInfo(name="Spring Boot"))

        # Check Flutter (via pubspec.yaml file detection or dependencies)
        has_flutter = any(f.endswith("pubspec.yaml") for f in files)
        if has_flutter:
            pubspec_path = os.path.join(workspace_path, "pubspec.yaml")
            if os.path.exists(pubspec_path):
                try:
                    with open(pubspec_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if "sdk: flutter" in content or "flutter:" in content:
                            frameworks.append(FrameworkInfo(name="Flutter"))
                except Exception:
                    pass

        # Check .NET (via .csproj file detection)
        has_dotnet = any(f.endswith(".csproj") for f in files)
        if has_dotnet:
            frameworks.append(FrameworkInfo(name=".NET"))

        return frameworks

    def detect_dependencies(self, workspace_path: str, files: List[str]) -> List[DependencyInfo]:
        """Parses manifest files extracting dependency definitions lists.

        Args:
            workspace_path: Root workspace path.
            files: Relative paths of all files in workspace.

        Returns:
            List of parsed DependencyInfo models.
        """
        dependencies = []

        for rel_path in files:
            abs_path = os.path.join(workspace_path, rel_path)
            fname = os.path.basename(rel_path)

            if not os.path.exists(abs_path):
                continue

            try:
                if fname == "requirements.txt":
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                        dependencies.extend(self._parse_requirements_txt(f.read()))

                elif fname == "pyproject.toml":
                    with open(abs_path, "rb") as f:
                        dependencies.extend(self._parse_pyproject_toml(f.read().decode("utf-8", errors="ignore")))

                elif fname == "poetry.lock":
                    with open(abs_path, "rb") as f:
                        dependencies.extend(self._parse_poetry_lock(f.read().decode("utf-8", errors="ignore")))

                elif fname == "package.json":
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                        dependencies.extend(self._parse_package_json(f.read()))

                elif fname == "package-lock.json":
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                        dependencies.extend(self._parse_package_lock_json(f.read()))

                elif fname == "pnpm-lock.yaml":
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                        dependencies.extend(self._parse_pnpm_lock_yaml(f.read()))

                elif fname == "yarn.lock":
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                        dependencies.extend(self._parse_yarn_lock(f.read()))

                elif fname == "Cargo.toml":
                    with open(abs_path, "rb") as f:
                        dependencies.extend(self._parse_cargo_toml(f.read().decode("utf-8", errors="ignore")))

                elif fname == "go.mod":
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                        dependencies.extend(self._parse_go_mod(f.read()))

                elif fname == "pom.xml":
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                        dependencies.extend(self._parse_pom_xml(f.read()))

                elif fname == "build.gradle":
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                        dependencies.extend(self._parse_build_gradle(f.read()))

                elif fname.endswith(".csproj"):
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                        dependencies.extend(self._parse_csproj(f.read()))

            except Exception:
                # Silently catch manifest parse failures to maintain robustness
                pass

        # De-duplicate dependencies on name+manager
        seen = set()
        unique_deps = []
        for d in dependencies:
            key = (d.name, d.manager)
            if key not in seen:
                seen.add(key)
                unique_deps.append(d)

        return unique_deps

    def _parse_requirements_txt(self, content: str) -> List[DependencyInfo]:
        deps = []
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-r"):
                continue
            match = re.match(r"^([a-zA-Z0-9_\-\[\]\.]+)(.*)$", line)
            if match:
                name, version_spec = match.groups()
                version = version_spec.strip() if version_spec else None
                # Clean up versions, e.g. ==1.0.0 -> 1.0.0
                if version and (version.startswith("==") or version.startswith(">=")):
                    version = re.sub(r"^[>=<~!]+", "", version).strip()
                deps.append(DependencyInfo(name=name, version=version or None, manager="pip"))
        return deps

    def _parse_pyproject_toml(self, content: str) -> List[DependencyInfo]:
        deps = []
        try:
            data = tomllib.loads(content)
            # Try PEP 621 dependencies
            project = data.get("project", {})
            if isinstance(project, dict):
                dependencies = project.get("dependencies", [])
                if isinstance(dependencies, list):
                    for dep in dependencies:
                        match = re.match(r"^([a-zA-Z0-9_\-\[\]\.]+)(.*)$", dep.strip())
                        if match:
                            name, version = match.groups()
                            v_str = re.sub(r"^[>=<~!]+", "", version).strip() if version else None
                            deps.append(DependencyInfo(name=name, version=v_str or None, manager="pip"))

            # Poetry dependencies
            tool = data.get("tool", {})
            if isinstance(tool, dict):
                poetry = tool.get("poetry", {})
                if isinstance(poetry, dict):
                    for dep_key in ["dependencies", "dev-dependencies", "group"]:
                        if dep_key == "group":
                            groups = poetry.get("group", {})
                            if isinstance(groups, dict):
                                for group_name, group_data in groups.items():
                                    group_deps = group_data.get("dependencies", {})
                                    if isinstance(group_deps, dict):
                                        for name, version in group_deps.items():
                                            if name.lower() == "python":
                                                continue
                                            v_str = str(version) if not isinstance(version, dict) else str(version.get("version", ""))
                                            v_str = re.sub(r"^[>=<~!^\s]+", "", v_str).strip()
                                            deps.append(DependencyInfo(name=name, version=v_str or None, manager="poetry"))
                        else:
                            poetry_deps = poetry.get(dep_key, {})
                            if isinstance(poetry_deps, dict):
                                for name, version in poetry_deps.items():
                                    if name.lower() == "python":
                                        continue
                                    v_str = str(version) if not isinstance(version, dict) else str(version.get("version", ""))
                                    v_str = re.sub(r"^[>=<~!^\s]+", "", v_str).strip()
                                    deps.append(DependencyInfo(name=name, version=v_str or None, manager="poetry"))
        except Exception:
            pass
        return deps

    def _parse_poetry_lock(self, content: str) -> List[DependencyInfo]:
        deps = []
        try:
            data = tomllib.loads(content)
            for package in data.get("package", []):
                name = package.get("name")
                version = package.get("version")
                if name:
                    deps.append(DependencyInfo(name=name, version=version, manager="poetry"))
        except Exception:
            pass
        return deps

    def _parse_package_json(self, content: str) -> List[DependencyInfo]:
        deps = []
        try:
            data = json.loads(content)
            for dep_type in ["dependencies", "devDependencies"]:
                if dep_type in data and isinstance(data[dep_type], dict):
                    for name, version in data[dep_type].items():
                        v_str = re.sub(r"^[>=<~!^\s]+", "", str(version)).strip()
                        deps.append(DependencyInfo(name=name, version=v_str or None, manager="npm"))
        except Exception:
            pass
        return deps

    def _parse_package_lock_json(self, content: str) -> List[DependencyInfo]:
        deps = []
        try:
            data = json.loads(content)
            packages = data.get("packages", {})
            if isinstance(packages, dict):
                for pkg_path, pkg_info in packages.items():
                    if not pkg_path:
                        continue
                    name = pkg_path.replace("node_modules/", "")
                    version = pkg_info.get("version")
                    if version:
                        deps.append(DependencyInfo(name=name, version=version, manager="npm"))
            else:
                dependencies = data.get("dependencies", {})
                if isinstance(dependencies, dict):
                    for name, info in dependencies.items():
                        version = info.get("version") if isinstance(info, dict) else str(info)
                        deps.append(DependencyInfo(name=name, version=version, manager="npm"))
        except Exception:
            pass
        return deps

    def _parse_pnpm_lock_yaml(self, content: str) -> List[DependencyInfo]:
        deps = []
        try:
            for line in content.splitlines():
                line = line.strip()
                # Matches format like: /accepts@1.3.8: or /accepts/1.3.8:
                match = re.match(r"^/?([a-zA-Z0-9_\-\.\[\]\/@]+)@([0-9\.\-a-zA-Z]+)(.*):$", line)
                if match:
                    name, version = match.groups()
                    if "/" in name and not name.startswith("@"):
                        name = name.split("/")[-1]
                    deps.append(DependencyInfo(name=name, version=version, manager="pnpm"))
        except Exception:
            pass
        return deps

    def _parse_yarn_lock(self, content: str) -> List[DependencyInfo]:
        deps = []
        try:
            current_name = None
            for line in content.splitlines():
                line_stripped = line.strip()
                if not line_stripped or line_stripped.startswith("#"):
                    continue
                if line_stripped.endswith(":") and not line.startswith(" "):
                    header = line_stripped[:-1]
                    parts = [p.strip().replace('"', '') for p in header.split(",")]
                    if parts:
                        first_part = parts[0]
                        if first_part.startswith("@"):
                            inner = first_part[1:]
                            if "@" in inner:
                                current_name = "@" + inner.split("@")[0]
                            else:
                                current_name = first_part
                        else:
                            current_name = first_part.split("@")[0]
                elif line_stripped.startswith("version ") and current_name:
                    version = line_stripped.split(" ", 1)[1].replace('"', '')
                    deps.append(DependencyInfo(name=current_name, version=version, manager="yarn"))
                    current_name = None
        except Exception:
            pass
        return deps

    def _parse_cargo_toml(self, content: str) -> List[DependencyInfo]:
        deps = []
        try:
            data = tomllib.loads(content)
            for section in ["dependencies", "dev-dependencies", "build-dependencies"]:
                val = data.get(section, {})
                if isinstance(val, dict):
                    for name, version in val.items():
                        v_str = str(version) if not isinstance(version, dict) else str(version.get("version", ""))
                        v_str = re.sub(r"^[>=<~!^\s]+", "", v_str).strip()
                        deps.append(DependencyInfo(name=name, version=v_str or None, manager="cargo"))
        except Exception:
            pass
        return deps

    def _parse_go_mod(self, content: str) -> List[DependencyInfo]:
        deps = []
        try:
            in_require = False
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("require ("):
                    in_require = True
                    continue
                if in_require and line.startswith(")"):
                    in_require = False
                    continue
                if line.startswith("require ") and not in_require:
                    parts = line.split()
                    if len(parts) >= 3:
                        deps.append(DependencyInfo(name=parts[1], version=parts[2], manager="go"))
                elif in_require and line:
                    parts = line.split()
                    if len(parts) >= 2:
                        deps.append(DependencyInfo(name=parts[0], version=parts[1], manager="go"))
        except Exception:
            pass
        return deps

    def _parse_pom_xml(self, content: str) -> List[DependencyInfo]:
        deps = []
        try:
            content_clean = re.sub(r'\sxmlns="[^"]+"', '', content, count=1)
            root = ET.fromstring(content_clean)
            for dependency in root.findall(".//dependency"):
                group_id = dependency.findtext("groupId")
                artifact_id = dependency.findtext("artifactId")
                version = dependency.findtext("version")
                if group_id and artifact_id:
                    deps.append(DependencyInfo(name=f"{group_id}:{artifact_id}", version=version, manager="maven"))
        except Exception:
            pass
        return deps

    def _parse_build_gradle(self, content: str) -> List[DependencyInfo]:
        deps = []
        try:
            pattern1 = re.compile(r"['\"]([^'\":]+):([^'\":]+):([^'\"]+)['\"]")
            for match in pattern1.finditer(content):
                group, artifact, version = match.groups()
                deps.append(DependencyInfo(name=f"{group}:{artifact}", version=version, manager="gradle"))
        except Exception:
            pass
        return deps

    def _parse_csproj(self, content: str) -> List[DependencyInfo]:
        deps = []
        try:
            root = ET.fromstring(content)
            for package_ref in root.findall(".//PackageReference"):
                include = package_ref.get("Include")
                version = package_ref.get("Version") or package_ref.findtext("Version")
                if include:
                    deps.append(DependencyInfo(name=include, version=version, manager="nuget"))
        except Exception:
            pass
        return deps
