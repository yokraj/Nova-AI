"""Modernizes syntax to leverage newer language features.
"""

import re
from app.agents.software_engineer.refactoring.interfaces import CodeModernizer
from app.agents.software_engineer.refactoring.models import ModernizationResult


class PythonSyntaxModernizer(CodeModernizer):
    """Replaces obsolete imports and structures."""

    def modernize_code(self, code: str) -> ModernizationResult:
        """Upgrades string formats and type annotations.

        Args:
            code: Source code string to modernize.

        Returns:
            ModernizationResult listing alterations.
        """
        features = []
        modernized = code

        # Replace Union[A, B] with A | B (simple regex matching)
        union_pattern = r"Union\s*\[\s*([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s*\]"
        if re.search(union_pattern, modernized):
            modernized = re.sub(union_pattern, r"\1 | \2", modernized)
            features.append("PEP 604 union types (A | B)")

        # Replace Optional[A] with A | None
        opt_pattern = r"Optional\s*\[\s*([a-zA-Z0-9_]+)\s*\]"
        if re.search(opt_pattern, modernized):
            modernized = re.sub(opt_pattern, r"\1 | None", modernized)
            features.append("PEP 604 optional types (A | None)")

        return ModernizationResult(
            success=True,
            features_upgraded=features,
        )
