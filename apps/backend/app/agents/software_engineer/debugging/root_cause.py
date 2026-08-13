"""Root Cause Analyzer tracing traceback stack frames to identify failure origin file and function scopes.
"""

import os
from typing import List

from app.agents.software_engineer.debugging.interfaces import RootCauseAnalyzer
from app.agents.software_engineer.debugging.models import DebugContext, RootCause, StackTrace


class TracebackRootCauseAnalyzer(RootCauseAnalyzer):
    """Traces stack frames to locate originating classes and scopes in the repository."""

    def detect_root_cause(
        self, traceback: StackTrace, context: DebugContext
    ) -> RootCause:
        """Locates the innermost workspace file frame from traceback listings.

        Args:
            traceback: Parsed StackTrace.
            context: Session context parameters.

        Returns:
            RootCause.
        """
        origin_file = "unknown"
        origin_function = "unknown"
        origin_class = None
        potential_causes = []

        # Trace from bottom (innermost call) upwards to find the first workspace file
        for frame in reversed(traceback.frames):
            # Check if file path is in the workspace
            is_in_workspace = (
                context.workspace_root in frame.file_path
                or "app/" in frame.file_path
                or "tests/" in frame.file_path
                or not os.path.isabs(frame.file_path)
            )

            if is_in_workspace and "site-packages" not in frame.file_path:
                origin_file = frame.file_path
                origin_function = frame.function_name
                break

        # Fallback to the last frame if none were resolved
        if origin_file == "unknown" and traceback.frames:
            origin_file = traceback.frames[-1].file_path
            origin_function = traceback.frames[-1].function_name

        # Guess potential causes based on exception message
        msg = traceback.exception_message.lower()
        if "none" in msg and "attribute" in msg:
            potential_causes.append("Null pointer access: attribute lookup on None object.")
        elif "key" in msg:
            potential_causes.append("Missing dictionary key.")
        elif "index" in msg:
            potential_causes.append("Index out of range.")
        elif "import" in msg or "module" in msg:
            potential_causes.append("Missing dependency or incorrect path syntax.")
        else:
            potential_causes.append(f"Runtime execution crashed: {traceback.exception_message}")

        return RootCause(
            origin_file=origin_file,
            origin_function=origin_function,
            origin_class=origin_class,
            failure_chain=[f.function_name for f in traceback.frames],
            affected_modules=[origin_file] if origin_file != "unknown" else [],
            potential_causes=potential_causes,
            confidence_score=0.9 if origin_file != "unknown" else 0.4,
        )
