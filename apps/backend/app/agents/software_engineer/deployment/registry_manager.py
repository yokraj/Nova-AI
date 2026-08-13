"""Registry Manager configures Docker registries tag options.
"""

class LocalRegistryManager:
    """Prepares Docker registry credentials templates and login parameters."""

    def generate_registry_config(self, project_name: str) -> str:
        """Returns repository tagging instructions guidelines."""
        name = project_name.lower().replace("_", "-")
        return f"""# Container Registry Push Guide for {project_name}

## Docker Hub
1. Authenticate locally:
   `docker login --username <username>`
2. Tag build target:
   `docker tag {name}:latest <username>/{name}:latest`
3. Push to hub:
   `docker push <username>/{name}:latest`

## AWS Elastic Container Registry (ECR)
1. Authenticate via AWS CLI:
   `aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com`
2. Create repo if needed:
   `aws ecr create-repository --repository-name {name}`
3. Tag image:
   `docker tag {name}:latest <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/{name}:latest`
4. Push:
   `docker push <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/{name}:latest`
"""
