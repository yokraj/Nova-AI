"""Exceptions for the Enterprise Software Deployment Engine.
"""

class DeploymentError(Exception):
    """Base exception for all deployment-related errors."""
    pass

class BuildError(DeploymentError):
    """Raised when application compilation, validation, or test execution fails."""
    pass

class ConfigurationError(DeploymentError):
    """Raised when environment variables, secrets, or deployment configs are invalid or missing."""
    pass

class ContainerGenerationError(DeploymentError):
    """Raised when generating Dockerfile or Docker Compose configurations fails."""
    pass

class PipelineError(DeploymentError):
    """Raised when generating CI/CD pipelines (GitHub Actions, GitLab CI, Jenkinsfile) fails."""
    pass

class ValidationError(DeploymentError):
    """Raised when post-generation or pre-deployment validations fail."""
    pass

class RollbackError(DeploymentError):
    """Raised when planning or executing deployment rollbacks fails."""
    pass

class ArtifactError(DeploymentError):
    """Raised when managing deployment artifacts or chart outputs fails."""
    pass
