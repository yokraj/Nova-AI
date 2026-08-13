"""Exception Analyzer auditing framework exceptions signatures.
"""

from app.agents.software_engineer.debugging.models import StackTrace


class FrameworkExceptionAnalyzer:
    """Classifies frameworks specific trace errors from FastAPI, SQLAlchemy, or Pydantic."""

    def analyze_exception(self, stacktrace: StackTrace) -> dict:
        """Determines details matching specific exception signatures.

        Args:
            stacktrace: Parsed StackTrace model.

        Returns:
            Dict containing diagnostics markers.
        """
        meta = {
            "framework": "unknown",
            "db_operational_error": False,
            "validation_failures_fields": [],
        }

        raw = stacktrace.raw_text

        # 1. Pydantic check
        if "ValidationError" in stacktrace.exception_type or "pydantic" in raw:
            meta["framework"] = "pydantic"
            # Extract failing validation fields if possible
            for line in raw.splitlines():
                if "  " in line and ":" in line and not line.strip().startswith("File "):
                    parts = line.strip().split(":")
                    if len(parts) > 1:
                        meta["validation_failures_fields"].append(parts[0].strip())

        # 2. SQLAlchemy check
        elif "sqlalchemy" in raw or "OperationalError" in stacktrace.exception_type:
            meta["framework"] = "sqlalchemy"
            meta["db_operational_error"] = True

        # 3. FastAPI check
        elif "fastapi" in raw or "starlette" in raw or "httpx" in raw:
            meta["framework"] = "fastapi"

        return meta
