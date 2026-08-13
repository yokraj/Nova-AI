"""Secret Manager manages configuration templates for credentials safely.
"""

from typing import List

class LocalSecretManager:
    """Provides placeholders and mapping details without storing active secrets."""

    def generate_secrets_template(self, env_vars: List[str]) -> str:
        """Generates a secure shell template recommending environment injection."""
        secret_vars = [v for v in env_vars if "key" in v.lower() or "secret" in v.lower() or "password" in v.lower() or "token" in v.lower()]
        
        lines = [
            "# ENVIRONMENT SECRETS TEMPLATE",
            "# Inject these variables dynamically inside your container environment or CI pipeline.",
            "# DO NOT COMMIT ACTUALLY ASSIGNED SECRETS IN PLAINTEXT TO Git VERSION CONTROL.",
            ""
        ]

        for s in secret_vars:
            lines.append(f"export {s}=\"$(op read 'op://vault/item/{s.lower()}')\" # Recommended 1Password CLI pattern")

        if not secret_vars:
            lines.append("export DB_PASSWORD=\"$(op read 'op://vault/item/database_password')\"")

        return "\n".join(lines)
