"""Environment Analyzer detects language, framework, dependencies, databases, and variables.
"""

import os
import re
from typing import List, Optional, Set
from app.agents.software_engineer.deployment.interfaces import IEnvironmentAnalyzer
from app.agents.software_engineer.deployment.models import EnvironmentInfo

class LocalEnvironmentAnalyzer(IEnvironmentAnalyzer):
    """Detects languages, frameworks, databases, and dependencies in target project path."""

    def analyze(self, project_path: str) -> EnvironmentInfo:
        """Scans the workspace directory to determine project configurations."""
        language = "Python"  # default fallback
        framework = None
        package_manager = "pip"
        runtime_version = "3.12"
        database = None
        env_vars: Set[str] = set()
        required_services: List[str] = []

        files = os.listdir(project_path) if os.path.exists(project_path) else []
        detected_docker_files = [f for f in files if "docker" in f.lower() or f.lower() == "dockerfile"]

        # 1. Detect language / package manager / files
        if "package.json" in files:
            language = "Node.js"
            package_manager = "npm"
            runtime_version = "20"
            content = self._read_file(os.path.join(project_path, "package.json"))
            if "react" in content:
                framework = "React"
            else:
                framework = "Node"
            
            # Detect DB
            if "pg" in content or "postgres" in content:
                database = "PostgreSQL"
                required_services.append("postgres")
            elif "mongodb" in content or "mongoose" in content:
                database = "MongoDB"
                required_services.append("mongodb")
            elif "redis" in content:
                database = "Redis"
                required_services.append("redis")

        elif "Cargo.toml" in files:
            language = "Rust"
            package_manager = "cargo"
            runtime_version = "1.80"
            content = self._read_file(os.path.join(project_path, "Cargo.toml"))
            if "tokio" in content:
                framework = "Tokio"
            if "sqlx" in content and "postgres" in content:
                database = "PostgreSQL"
                required_services.append("postgres")

        elif "pom.xml" in files:
            language = "Java"
            package_manager = "maven"
            runtime_version = "17"
            framework = "Spring Boot"
            content = self._read_file(os.path.join(project_path, "pom.xml"))
            if "postgresql" in content:
                database = "PostgreSQL"
                required_services.append("postgres")
            elif "mysql" in content:
                database = "MySQL"
                required_services.append("mysql")

        elif "go.mod" in files:
            language = "Go"
            package_manager = "go"
            runtime_version = "1.22"
            content = self._read_file(os.path.join(project_path, "go.mod"))
            if "gin" in content:
                framework = "Gin"
            elif "fiber" in content:
                framework = "Fiber"

        else:
            # Python check
            language = "Python"
            if "pyproject.toml" in files:
                package_manager = "poetry"
                content = self._read_file(os.path.join(project_path, "pyproject.toml"))
            elif "requirements.txt" in files:
                package_manager = "pip"
                content = self._read_file(os.path.join(project_path, "requirements.txt"))
            else:
                package_manager = "pip"
                content = ""

            if "fastapi" in content.lower():
                framework = "FastAPI"
            elif "django" in content.lower():
                framework = "Django"
            elif "flask" in content.lower():
                framework = "Flask"

            # DB checks
            if "psycopg" in content.lower() or "asyncpg" in content.lower():
                database = "PostgreSQL"
                required_services.append("postgres")
            elif "redis" in content.lower():
                database = "Redis"
                required_services.append("redis")
            elif "mysql" in content.lower():
                database = "MySQL"
                required_services.append("mysql")

        # 2. Extract Env Variables (scan source files recursively)
        env_pattern_py = re.compile(r"os\.environ\.get\(['\"]([A-Z0-9_]+)['\"]\)")
        env_pattern_js = re.compile(r"process\.env\.([A-Z0-9_]+)")
        
        for root, _, filenames in os.walk(project_path):
            if any(ignore in root for ignore in [".git", ".venv", "node_modules", "build", "dist"]):
                continue
            for f in filenames:
                if f.endswith((".py", ".js", ".ts", ".tsx", ".java", ".go", ".rs")):
                    file_content = self._read_file(os.path.join(root, f))
                    for var in env_pattern_py.findall(file_content):
                        env_vars.add(var)
                    for var in env_pattern_js.findall(file_content):
                        env_vars.add(var)

        # Standard environment var templates fallback
        if not env_vars:
            env_vars.update(["DATABASE_URL", "PORT", "SECRET_KEY", "ENVIRONMENT"])

        return EnvironmentInfo(
            language=language,
            framework=framework,
            runtime_version=runtime_version,
            package_manager=package_manager,
            database=database,
            env_vars=sorted(list(env_vars)),
            required_services=required_services,
            docker_files=detected_docker_files,
        )

    def _read_file(self, path: str) -> str:
        if not os.path.exists(path):
            return ""
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""
