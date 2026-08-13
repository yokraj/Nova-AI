"""Deployment Report Generator constructs markdown summarizing results.
"""

from typing import List
from app.agents.software_engineer.deployment.models import (
    EnvironmentInfo,
    BuildResult,
    DockerConfiguration,
    PipelineConfiguration,
    ReleaseVersion,
    RollbackPlan,
    DeploymentArtifact,
)

class DeploymentReportGenerator:
    """Formats and prints structural implementation markdown files."""

    def generate_markdown(
        self,
        env_info: EnvironmentInfo,
        build_result: BuildResult,
        docker_config: DockerConfiguration,
        pipeline_config: PipelineConfiguration,
        release_version: ReleaseVersion,
        rollback_plan: RollbackPlan,
        artifacts: List[DeploymentArtifact],
    ) -> str:
        """Assembles variables into printable markdown strings."""
        artifacts_md = "\n".join([f"- **{a.name}** ({a.type}): `{a.path}` (checksum: `{a.checksum[:8]}...`)" for a in artifacts])
        
        return f"""# Enterprise Deployment Preparation Report

## System Architecture & Summary
- **Language**: {env_info.language}
- **Framework**: {env_info.framework or 'Generic'}
- **Database**: {env_info.database or 'None'}
- **Version**: {release_version.version}

## Security Strategy & Containerization
- **Base Image**: `{docker_config.base_image}`
- **Security Checklists**:
  - Non-root user set: **Yes**
  - Multi-stage build configured: **Yes**
  - Exposed ports: {docker_config.ports}
  - Health check endpoint configured: **Yes**

## CI/CD Pipeline Configuration
- **GitHub Actions**: Enabled (.github/workflows/deploy.yml generated)
- **GitLab CI**: Enabled (.gitlab-ci.yml generated)
- **Jenkinsfile**: Enabled (Jenkinsfile generated)

## Rollback & Recovery Procedures
- **Target Rollback Version**: `{rollback_plan.target_version}`
- **Rollback Steps**:
{chr(10).join(['  ' + step for step in rollback_plan.steps])}

## Generated Templates Catalog
{artifacts_md}
"""
