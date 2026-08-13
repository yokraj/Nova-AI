"""StackTrace Parser extracting file paths, line numbers, and exception messages from traceback logs.
"""

import re
from typing import List

from app.agents.software_engineer.debugging.interfaces import StackTraceParser
from app.agents.software_engineer.debugging.models import StackFrame, StackTrace


class PythonStackTraceParser(StackTraceParser):
    """Regex-based parser for standard Python trace logs."""

    def parse_traceback(self, traceback_str: str) -> StackTrace:
        """Parses traceback frames.

        Args:
            traceback_str: Raw traceback logs.

        Returns:
            StackTrace.
        """
        frames: List[StackFrame] = []
        lines = traceback_str.splitlines()

        # Regex mapping: File "...", line ..., in ...
        frame_pattern = re.compile(r'File "([^"]+)", line (\d+), in (\w+)(?:\s*\n\s*(.*))?')

        for idx, line in enumerate(lines):
            match = re.search(r'File "([^"]+)", line (\d+), in (\w+)', line)
            if match:
                file_path, line_num, func = match.groups()
                code_line = ""
                # Try getting the next line containing the code statement
                if idx + 1 < len(lines) and not lines[idx + 1].strip().startswith("File "):
                    code_line = lines[idx + 1].strip()

                frames.append(
                    StackFrame(
                        file_path=file_path,
                        line_number=int(line_num),
                        function_name=func,
                        code_line=code_line,
                    )
                )

        # Infer exception type and message from the last line
        exc_type = "RuntimeError"
        exc_msg = "Unknown execution exception error."

        for line in reversed(lines):
            line_strip = line.strip()
            if not line_strip:
                continue
            # Look for lines like "NameError: name 'x' is not defined" or similar
            match_exc = re.match(r"^([A-Za-z0-9_.]+Error|Exception|KeyError):\s*(.*)", line_strip)
            if match_exc:
                exc_type, exc_msg = match_exc.groups()
                break

        return StackTrace(
            raw_text=traceback_str,
            frames=frames,
            exception_type=exc_type,
            exception_message=exc_msg,
        )
