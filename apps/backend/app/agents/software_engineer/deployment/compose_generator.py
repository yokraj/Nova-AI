"""Docker Compose Generator drafts docker-compose configurations.
"""

from typing import List, Optional

class DockerComposeGenerator:
    """Generates compose yaml structure matching framework and backing databases."""

    def generate_compose(self, framework: str, database: Optional[str] = None, services: Optional[List[str]] = None) -> str:
        """Returns docker-compose.yml contents."""
        services = services or []
        db_service_yaml = ""
        db_env_yaml = ""
        depends_on_yaml = ""

        if database == "PostgreSQL":
            depends_on_yaml = "\n    depends_on:\n      - db"
            db_env_yaml = "\n      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app"
            db_service_yaml = """
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
"""

        elif database == "MongoDB":
            depends_on_yaml = "\n    depends_on:\n      - mongodb"
            db_env_yaml = "\n      - DATABASE_URL=mongodb://mongodb:27017/app"
            db_service_yaml = """
  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongodata:/data/db
"""

        redis_service_yaml = ""
        if "redis" in services:
            redis_service_yaml = """
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
"""

        volumes_section = ""
        if database == "PostgreSQL":
            volumes_section = "\nvolumes:\n  pgdata:\n"
        elif database == "MongoDB":
            volumes_section = "\nvolumes:\n  mongodata:\n"

        framework_port = 8000
        if (framework or "").lower() == "spring boot":
            framework_port = 8080
        elif (framework or "").lower() == "react":
            framework_port = 80

        return f"""version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "{framework_port}:{framework_port}"
    environment:
      - ENVIRONMENT=production{db_env_yaml}{depends_on_yaml}
{db_service_yaml}{redis_service_yaml}{volumes_section}"""
