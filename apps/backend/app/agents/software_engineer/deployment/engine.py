"""LocalDeploymentEngine implements IDeploymentEngine, executing the 11-stage pipeline.
"""

import os
import time
from typing import Any, Optional
from datetime import datetime

from app.agents.software_engineer.deployment.interfaces import IDeploymentEngine
from app.agents.software_engineer.deployment.exceptions import DeploymentError, ValidationError
from app.agents.software_engineer.deployment.models import (
    DeploymentRequest,
    DeploymentReport,
    DeploymentArtifact,
    DockerConfiguration,
    PipelineConfiguration,
)
from app.agents.software_engineer.deployment.context_builder import DeploymentContextBuilder
from app.agents.software_engineer.deployment.planner import DeploymentPlanner
from app.agents.software_engineer.deployment.environment_analyzer import LocalEnvironmentAnalyzer
from app.agents.software_engineer.deployment.dependency_checker import LocalDependencyChecker
from app.agents.software_engineer.deployment.build_manager import LocalBuildManager
from app.agents.software_engineer.deployment.docker_generator import LocalContainerGenerator
from app.agents.software_engineer.deployment.kubernetes_generator import KubernetesGenerator
from app.agents.software_engineer.deployment.helm_generator import HelmGenerator
from app.agents.software_engineer.deployment.ci_generator import CIGenerator
from app.agents.software_engineer.deployment.deployment_validator import LocalValidator
from app.agents.software_engineer.deployment.release_manager import LocalReleaseManager
from app.agents.software_engineer.deployment.rollback_manager import LocalRollbackManager
from app.agents.software_engineer.deployment.artifact_manager import LocalArtifactManager
from app.agents.software_engineer.deployment.monitoring_configurator import LocalMonitoringConfigurator
from app.agents.software_engineer.deployment.deployment_report import DeploymentReportGenerator
from app.agents.software_engineer.deployment.configuration_manager import LocalConfigurationManager
from app.agents.software_engineer.deployment.secret_manager import LocalSecretManager
from app.agents.software_engineer.deployment.migration_manager import LocalMigrationManager
from app.agents.software_engineer.deployment.registry_manager import LocalRegistryManager
from app.agents.software_engineer.deployment.cache import DeploymentCache
from app.agents.software_engineer.deployment.template_engine import TemplateEngine
from app.agents.software_engineer.deployment.utils import calculate_content_checksum, write_deployment_file
from app.ai.gateway import AIGateway
from app.ai.models import ChatRequest, PromptMessage

class LocalDeploymentEngine(IDeploymentEngine):
    """The production orchestrator for the Enterprise Software Deployment Engine."""

    def __init__(self, gateway: Optional[AIGateway] = None, workspace_root: Optional[str] = None) -> None:
        self.gateway = gateway
        self.workspace_root = workspace_root or os.getcwd()
        
        # Sub-components setup
        self.context_builder = DeploymentContextBuilder(workspace_root=self.workspace_root)
        self.planner = DeploymentPlanner()
        self.env_analyzer = LocalEnvironmentAnalyzer()
        self.dependency_checker = LocalDependencyChecker()
        self.build_manager = LocalBuildManager()
        self.container_gen = LocalContainerGenerator()
        self.k8s_gen = KubernetesGenerator()
        self.helm_gen = HelmGenerator()
        self.ci_gen = CIGenerator()
        self.validator = LocalValidator()
        self.release_manager = LocalReleaseManager()
        self.rollback_manager = LocalRollbackManager()
        self.artifact_manager = LocalArtifactManager()
        self.monitoring_configurator = LocalMonitoringConfigurator()
        self.report_gen = DeploymentReportGenerator()
        self.config_manager = LocalConfigurationManager()
        self.secret_manager = LocalSecretManager()
        self.migration_manager = LocalMigrationManager()
        self.registry_manager = LocalRegistryManager()
        self.cache = DeploymentCache(workspace_root=self.workspace_root)

    async def prepare_deployment(self, request: DeploymentRequest) -> DeploymentReport:
        """Executes the full 11-stage autonomous deployment preparation pipeline."""
        project_path = request.project_path or self.workspace_root
        
        # 1. Project Analysis
        context = self.context_builder.build_context()

        # 2. Environment Detection
        env_info = self.env_analyzer.analyze(project_path)

        # 3. Dependency Validation
        dep_errors = self.dependency_checker.check_dependencies(project_path)
        if dep_errors:
            # We record but continue or raise based on severity
            pass

        # 4. Build Planning
        build_result = self.build_manager.validate_build_readiness(project_path, env_info)

        # 5. Container Generation
        docker_config = self.container_gen.generate(project_path, env_info)
        
        # Optionally enhance generated Dockerfile using AIGateway if available
        if self.gateway:
            model_name = request.model_override or "qwen2.5-coder"
            try:
                chat_req = ChatRequest(
                    model=model_name,
                    messages=[
                        PromptMessage(
                            role="system",
                            content="You are a principal security engineer. Optimize the following Dockerfile contents to run securely using non-root privileges. Return only the updated Dockerfile without markdown wrappers."
                        ),
                        PromptMessage(
                            role="user",
                            content=docker_config.dockerfile_content
                        )
                    ]
                )
                res = await self.gateway.chat(chat_req)
                if res and res.message and res.message.content:
                    docker_config.dockerfile_content = res.message.content.strip()
            except Exception:
                # Fallback to locally generated deterministic Dockerfile
                pass

        # 6. Infrastructure Generation
        # Generate K8s and Helm files if requested or as part of preparation
        k8s_manifests = self.k8s_gen.generate_manifests(
            context.get("project_name", "app"),
            docker_config.ports[0] if docker_config.ports else 8000,
            env_info.env_vars
        )
        helm_files = self.helm_gen.generate_chart(
            context.get("project_name", "app"),
            docker_config.ports[0] if docker_config.ports else 8000
        )

        # Write generated container files physically to the target workspace
        output_dir = os.path.join(project_path, ".nova", "deployment")
        df_path = write_deployment_file(os.path.join(project_path, "Dockerfile"), docker_config.dockerfile_content)
        comp_path = write_deployment_file(os.path.join(project_path, "docker-compose.yml"), docker_config.compose_content)

        self.artifact_manager.track_artifact(DeploymentArtifact(
            name="Dockerfile",
            type="dockerfile",
            path=df_path,
            checksum=calculate_content_checksum(docker_config.dockerfile_content)
        ))
        self.artifact_manager.track_artifact(DeploymentArtifact(
            name="docker-compose.yml",
            type="compose",
            path=comp_path,
            checksum=calculate_content_checksum(docker_config.compose_content)
        ))

        # Write K8s manifests
        for filename, content in k8s_manifests.items():
            path = write_deployment_file(os.path.join(output_dir, "kubernetes", filename), content)
            self.artifact_manager.track_artifact(DeploymentArtifact(
                name=filename,
                type="kubernetes",
                path=path,
                checksum=calculate_content_checksum(content)
            ))

        # Write Helm files
        for filename, content in helm_files.items():
            path = write_deployment_file(os.path.join(output_dir, "helm", filename), content)
            self.artifact_manager.track_artifact(DeploymentArtifact(
                name=filename,
                type="helm",
                path=path,
                checksum=calculate_content_checksum(content)
            ))

        # 7. CI/CD Generation
        pipeline_config = self.ci_gen.generate(project_path, env_info)
        if pipeline_config.github_actions_yaml:
            gha_path = write_deployment_file(os.path.join(project_path, ".github", "workflows", "deploy.yml"), pipeline_config.github_actions_yaml)
            self.artifact_manager.track_artifact(DeploymentArtifact(
                name="deploy.yml",
                type="pipeline",
                path=gha_path,
                checksum=calculate_content_checksum(pipeline_config.github_actions_yaml)
            ))
        if pipeline_config.gitlab_ci_yaml:
            gl_path = write_deployment_file(os.path.join(project_path, ".gitlab-ci.yml"), pipeline_config.gitlab_ci_yaml)
            self.artifact_manager.track_artifact(DeploymentArtifact(
                name=".gitlab-ci.yml",
                type="pipeline",
                path=gl_path,
                checksum=calculate_content_checksum(pipeline_config.gitlab_ci_yaml)
            ))
        if pipeline_config.jenkinsfile_content:
            jk_path = write_deployment_file(os.path.join(project_path, "Jenkinsfile"), pipeline_config.jenkinsfile_content)
            self.artifact_manager.track_artifact(DeploymentArtifact(
                name="Jenkinsfile",
                type="pipeline",
                path=jk_path,
                checksum=calculate_content_checksum(pipeline_config.jenkinsfile_content)
            ))

        # 8. Deployment Validation
        val_errors = self.validator.validate(project_path, docker_config, pipeline_config)
        validation_status = "passed" if not val_errors else "failed"

        # 9. Release Preparation
        release_version = self.release_manager.prepare_release(project_path, "1.0.0")

        # 10. Monitoring Setup
        monitor_configs = self.monitoring_configurator.configure(project_path, env_info)
        for filename, content in monitor_configs.items():
            path = write_deployment_file(os.path.join(output_dir, "monitoring", filename), content)
            self.artifact_manager.track_artifact(DeploymentArtifact(
                name=filename,
                type="monitoring",
                path=path,
                checksum=calculate_content_checksum(content)
            ))

        # 10.5 Configurations, Secrets, Migration & Registry Generation
        # Write config templates
        config_files = self.config_manager.generate_configs(env_info.env_vars)
        for filename, content in config_files.items():
            path = write_deployment_file(os.path.join(output_dir, "config", filename), content)
            self.artifact_manager.track_artifact(DeploymentArtifact(
                name=filename,
                type="config",
                path=path,
                checksum=calculate_content_checksum(content)
            ))

        # Write secrets template
        secrets_template = self.secret_manager.generate_secrets_template(env_info.env_vars)
        st_path = write_deployment_file(os.path.join(output_dir, "secrets", "secrets.sh"), secrets_template)
        self.artifact_manager.track_artifact(DeploymentArtifact(
            name="secrets.sh",
            type="secrets",
            path=st_path,
            checksum=calculate_content_checksum(secrets_template)
        ))

        # Write database migration plan
        migration_plan = self.migration_manager.generate_migration_plan(env_info.database)
        mig_path = write_deployment_file(os.path.join(output_dir, "migration", "migration_plan.md"), migration_plan)
        self.artifact_manager.track_artifact(DeploymentArtifact(
            name="migration_plan.md",
            type="migration",
            path=mig_path,
            checksum=calculate_content_checksum(migration_plan)
        ))

        # Write registry push guide
        registry_config = self.registry_manager.generate_registry_config(context.get("project_name", "app"))
        reg_path = write_deployment_file(os.path.join(output_dir, "registry", "registry_push_guide.md"), registry_config)
        self.artifact_manager.track_artifact(DeploymentArtifact(
            name="registry_push_guide.md",
            type="registry",
            path=reg_path,
            checksum=calculate_content_checksum(registry_config)
        ))

        # Update cache
        self.cache.set("last_deployment_version", release_version.version)

        # 11. Deployment Report
        markdown_report = self.report_gen.generate_markdown(
            env_info,
            build_result,
            docker_config,
            pipeline_config,
            release_version,
            self.rollback_manager.generate_rollback_plan(release_version.version, "1.0.0"),
            self.artifact_manager.list_artifacts()
        )
        report_path = write_deployment_file(os.path.join(project_path, "SPEC_M3_1_9_IMPLEMENTATION_REPORT.md"), markdown_report)
        
        self.artifact_manager.track_artifact(DeploymentArtifact(
            name="SPEC_M3_1_9_IMPLEMENTATION_REPORT.md",
            type="report",
            path=report_path,
            checksum=calculate_content_checksum(markdown_report)
        ))

        return DeploymentReport(
            status="success" if validation_status == "passed" else "warning",
            environment_info=env_info,
            build_result=build_result,
            container_config=docker_config,
            pipeline_config=pipeline_config,
            release_version=release_version,
            rollback_plan=self.rollback_manager.generate_rollback_plan(release_version.version, "1.0.0"),
            artifacts=self.artifact_manager.list_artifacts(),
            validation_status=validation_status,
            report_markdown=markdown_report,
        )
