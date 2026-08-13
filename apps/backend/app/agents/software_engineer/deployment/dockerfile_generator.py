"""Dockerfile Generator produces secure, multi-stage, non-root container configurations.
"""

from typing import Dict, Any

class DockerfileGenerator:
    """Generates Dockerfiles based on detected language and framework."""

    def generate_dockerfile(self, framework: str, version: str) -> str:
        """Returns Dockerfile content matching framework requirements."""
        framework_lower = (framework or "").lower()

        if "fastapi" in framework_lower or "flask" in framework_lower or "django" in framework_lower:
            return self._python_dockerfile(framework_lower)
        elif "react" in framework_lower:
            return self._react_dockerfile()
        elif "node" in framework_lower or "express" in framework_lower:
            return self._node_dockerfile()
        elif "spring" in framework_lower:
            return self._spring_boot_dockerfile()
        else:
            # Python generic fallback
            return self._python_dockerfile("generic")

    def _python_dockerfile(self, framework: str) -> str:
        entrypoint = "uvicorn app.main:app --host 0.0.0.0 --port 8000"
        if framework == "django":
            entrypoint = "python manage.py runserver 0.0.0.0:8000"
        elif framework == "flask":
            entrypoint = "python -m flask run --host=0.0.0.0 --port=8000"

        return f"""# Multi-stage Python build
FROM python:3.12-slim AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim AS runner
WORKDIR /app

RUN groupadd -g 10001 appuser && useradd -u 10001 -g appuser appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY . .

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

ENTRYPOINT ["sh", "-c", "{entrypoint}"]
"""

    def _react_dockerfile(self) -> str:
        return """# Multi-stage Node/React build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine-slim AS runner
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
"""

    def _node_dockerfile(self) -> str:
        return """# Multi-stage Node.js build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

FROM node:20-alpine AS runner
WORKDIR /app
RUN addgroup -g 10001 -S appgroup && adduser -u 10001 -S appuser -G appgroup
COPY --from=builder /app /app
ENV PORT=3000
EXPOSE 3000
USER appuser
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => { if (r.statusCode === 200) process.exit(0); else process.exit(1); })" || exit 1
CMD ["npm", "start"]
"""

    def _spring_boot_dockerfile(self) -> str:
        return """# Multi-stage Java build
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-jammy AS runner
WORKDIR /app
RUN groupadd -g 10001 appuser && useradd -u 10001 -g appuser appuser
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
USER appuser
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1
ENTRYPOINT ["java", "-jar", "app.jar"]
"""
