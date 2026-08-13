"""Failure Classifier mapping exceptions types to standard diagnostic categories.
"""

from app.agents.software_engineer.debugging.interfaces import FailureClassifier
from app.agents.software_engineer.debugging.models import FailureClassification, StackTrace


class TraceFailureClassifier(FailureClassifier):
    """Categorizes stack trace failures into standard categories."""

    def classify_failure(self, traceback: StackTrace) -> FailureClassification:
        """Determines category based on exception names.

        Args:
            traceback: Parsed traceback.

        Returns:
            FailureClassification.
        """
        category = "unknown"
        explanation = f"Generic error of type {traceback.exception_type}."

        exc_type = traceback.exception_type

        if exc_type in ("SyntaxError", "IndentationError", "TabError"):
            category = "syntax"
            explanation = "Syntax error in python code. Failed to compile AST structure."
        elif exc_type in ("ImportError", "ModuleNotFoundError"):
            category = "import"
            explanation = "Failed to locate Python module or package from local import paths."
        elif exc_type in ("ConnectionError", "TimeoutError") or "http" in traceback.raw_text.lower():
            category = "api"
            explanation = "Failed network HTTP call request."
        elif exc_type in ("OperationalError", "IntegrityError", "ProgrammingError") or "sqlalchemy" in traceback.raw_text.lower():
            category = "database"
            explanation = "Database operational failure or query validation crash."
        elif exc_type in ("KeyError", "IndexError", "TypeError", "ValueError", "AttributeError"):
            category = "logic"
            explanation = "Application logic bug (null reference, missing dictionary keys, or parameter mismatch)."
        elif exc_type == "MemoryError":
            category = "performance"
            explanation = "Out of memory error."
        else:
            category = "runtime"
            explanation = "Generic application execution crashed."

        return FailureClassification(category=category, explanation=explanation)
