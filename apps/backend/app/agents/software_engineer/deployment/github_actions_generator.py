"""GitHub Actions Generator designs GHA YAML pipeline workflows.
"""

from typing import List

class GitHubActionsGenerator:
    """Generates GitHub Actions workflows targeting various language/framework projects."""

    def generate_pipeline(self, project_name: str, language: str, package_manager: str) -> str:
        """Returns .github/workflows/deploy.yml contents."""
        setup_steps = ""
        test_cmd = "echo 'No tests defined'"
        lint_cmd = "echo 'No lint defined'"
        build_cmd = "echo 'No build step'"

        if language == "Python":
            setup_steps = """      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'"""
            if package_manager == "poetry":
                setup_steps = """      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install Poetry
        run: pipx install poetry
      - name: Install dependencies
        run: poetry install"""
                test_cmd = "poetry run pytest"
                lint_cmd = "poetry run ruff check ."
            else:
                setup_steps = """      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install ruff pytest
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi"""
                test_cmd = "pytest"
                lint_cmd = "ruff check ."

        elif language == "Node.js":
            setup_steps = """      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - name: Install dependencies
        run: npm ci"""
            test_cmd = "npm test"
            lint_cmd = "npm run lint || echo 'No lint command'"
            build_cmd = "npm run build --if-present"

        return f"""name: CI/CD Pipeline

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
      - name: Code Checkout
        uses: actions/checkout@v4

{setup_steps}

      - name: Lint
        run: {lint_cmd}

      - name: Testing
        run: {test_cmd}

      - name: Build
        run: {build_cmd}

      - name: Security Scan
        uses: securego/gosec@master
        with:
          args: ./...
        continue-on-error: true

      - name: Docker Build
        run: |
          docker build -t {project_name.lower()}:latest .

      - name: Deploy
        run: |
          echo "Deploying to production target..."
"""
