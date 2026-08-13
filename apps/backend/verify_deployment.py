"""Lightweight verification script for the Enterprise Software Deployment Engine.
"""

import os
import asyncio
import shutil
import tempfile
from app.agents.software_engineer.deployment.engine import LocalDeploymentEngine
from app.agents.software_engineer.deployment.models import DeploymentRequest

async def verify_deployment_engine():
    print("=== STARTING DEPLOYMENT ENGINE VERIFICATION ===")

    # 1. Create a dummy project directory to run environment detection
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Creating dummy project in: {temp_dir}")
        
        # Write requirements.txt with FastAPI
        requirements_path = os.path.join(temp_dir, "requirements.txt")
        with open(requirements_path, "w", encoding="utf-8") as f:
            f.write("fastapi>=0.110.0\npsycopg2-binary>=2.9.9\n")

        # Write dummy python file using os.environ
        app_py = os.path.join(temp_dir, "main.py")
        with open(app_py, "w", encoding="utf-8") as f:
            f.write("""import os\nPORT = os.environ.get("APP_PORT", 8080)\nDATABASE_URL = os.environ.get("DATABASE_URL")\n""")

        # 2. Instantiate local engine
        engine = LocalDeploymentEngine(gateway=None, workspace_root=temp_dir)

        # 3. Form request
        request = DeploymentRequest(
            project_path=temp_dir,
            environment="production",
            target_platform="kubernetes"
        )

        # 4. Run pipeline
        print("Executing deployment preparation pipeline...")
        report = await engine.prepare_deployment(request)

        # 5. Asserts and validations
        print("Running validation assertions...")
        
        # Validate Environment Detection
        assert report.environment_info.language == "Python", f"Expected Python, got {report.environment_info.language}"
        assert report.environment_info.framework == "FastAPI", f"Expected FastAPI, got {report.environment_info.framework}"
        assert "postgres" in report.environment_info.required_services, "Expected PostgreSQL service dependency"
        assert "DATABASE_URL" in report.environment_info.env_vars, "Expected DATABASE_URL in env vars"
        print("✓ Environment analysis verified successfully.")

        # Validate Docker generation
        assert "FROM python:3.12-slim" in report.container_config.dockerfile_content, "Missing secure base image in Dockerfile"
        assert "USER appuser" in report.container_config.dockerfile_content, "Missing security non-root appuser directive"
        assert "HEALTHCHECK" in report.container_config.dockerfile_content, "Missing health check block in Dockerfile"
        assert "web:" in report.container_config.compose_content, "Missing web service configuration in docker-compose.yml"
        assert "db:" in report.container_config.compose_content, "Missing db backing service configuration in docker-compose.yml"
        print("✓ Docker and compose configuration generated and verified successfully.")

        # Validate CI Pipeline generation
        assert report.pipeline_config.github_actions_yaml is not None, "GitHub Actions workflow not generated"
        assert "Lint" in report.pipeline_config.github_actions_yaml, "Missing Lint step in pipeline workflow"
        assert "Testing" in report.pipeline_config.github_actions_yaml, "Missing Testing step in pipeline workflow"
        assert "Security Scan" in report.pipeline_config.github_actions_yaml, "Missing Security Scan step in pipeline workflow"
        assert "docker build" in report.pipeline_config.github_actions_yaml.lower(), "Missing Docker Build step in pipeline workflow"
        print("✓ CI/CD pipeline generation verified successfully.")

        # Validate Rollback planning
        assert report.rollback_plan.target_version == "1.0.0", "Incorrect rollback target version"
        assert len(report.rollback_plan.steps) > 0, "No rollback steps compiled"
        print("✓ Rollback plan generation verified successfully.")

        # Validate Configuration templates
        configs = [a.name for a in report.artifacts]
        assert "Dockerfile" in configs, "Dockerfile not cataloged in artifacts list"
        assert "docker-compose.yml" in configs, "docker-compose.yml not cataloged in artifacts list"
        assert "configmap.yaml" in configs, "K8s ConfigMap config not cataloged in artifacts list"
        assert "secrets.yaml" in configs, "K8s Secrets config not cataloged in artifacts list"
        print("✓ Deployment configuration artifacts tracked and verified successfully.")

        # Validate Reports
        assert report.report_markdown != "", "Empty report markdown generated"
        assert "## Security Strategy" in report.report_markdown, "Missing Security Strategy section in report markdown"
        assert "## CI/CD Pipeline" in report.report_markdown, "Missing CI/CD Pipeline section in report markdown"
        print("✓ Deployment report generated and verified successfully.")

        print("=== DEPLOYMENT ENGINE VERIFICATION PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    asyncio.run(verify_deployment_engine())
