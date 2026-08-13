"""Configuration Manager handles environment templates and .env generation.
"""

from typing import Dict, List

class LocalConfigurationManager:
    """Creates local configuration templates and environment profiles."""

    def generate_configs(self, env_vars: List[str]) -> Dict[str, str]:
        """Generates configuration content for dev, prod, and testing."""
        configs = {}
        
        # Build standard key-value defaults
        dev_vars = []
        prod_vars = []
        test_vars = []
        example_vars = []

        for var in env_vars:
            example_vars.append(f"{var}=")
            if "env" in var.lower():
                dev_vars.append(f"{var}=development")
                prod_vars.append(f"{var}=production")
                test_vars.append(f"{var}=testing")
            elif "port" in var.lower():
                dev_vars.append(f"{var}=8000")
                prod_vars.append(f"{var}=80")
                test_vars.append(f"{var}=8001")
            elif "debug" in var.lower():
                dev_vars.append(f"{var}=True")
                prod_vars.append(f"{var}=False")
                test_vars.append(f"{var}=True")
            elif "db" in var.lower() or "database" in var.lower():
                dev_vars.append(f"{var}=postgresql://postgres:postgres@localhost:5432/dev_db")
                prod_vars.append(f"{var}=postgresql://postgres:prod_pass@prod-db-host:5432/prod_db")
                test_vars.append(f"{var}=sqlite:///:memory:")
            else:
                dev_vars.append(f"{var}=dev_value")
                prod_vars.append(f"{var}=prod_value")
                test_vars.append(f"{var}=test_value")

        configs[".env.example"] = "\n".join(example_vars)
        configs[".env.development"] = "\n".join(dev_vars)
        configs[".env.production"] = "\n".join(prod_vars)
        configs[".env.testing"] = "\n".join(test_vars)

        return configs
