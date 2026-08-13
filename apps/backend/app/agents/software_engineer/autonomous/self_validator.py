"""Self Validator compiles Quality Gate reports.
"""

import os
from app.agents.software_engineer.autonomous.interfaces import IValidator
from app.agents.software_engineer.autonomous.models import ExecutionContext, QualityReport
from app.agents.software_engineer.autonomous.quality_gate import QualityGate

class LocalSelfValidator(IValidator):
    """Encapsulates validation processes targeting codebase files."""

    def __init__(self) -> None:
        self.gate = QualityGate()

    def validate_gates(self, context: ExecutionContext) -> QualityReport:
        """Executes validations, reading files list from workspace root."""
        files = []
        try:
            for root, _, filenames in os.walk(context.workspace_root):
                if any(i in root for i in [".git", ".venv", "node_modules", "build"]):
                    continue
                for f in filenames:
                    files.append(os.path.join(root, f))
        except Exception:
            pass

        return self.gate.validate_all_gates(context.workspace_root, files)
