"""Security Scanner detecting SQL injection and hardcoded secrets.
"""

import re
from typing import List

from app.agents.software_engineer.testing.interfaces import SecurityScanner
from app.agents.software_engineer.testing.models import SecurityFinding


class StaticSecurityScanner(SecurityScanner):
    """Parses Python source file strings looking for security concerns."""

    def scan_security(self, workspace_path: str, file_path: str) -> List[SecurityFinding]:
        """Runs checks to identify hardcoded passwords, dangerous function calls.

        Args:
            workspace_path: Absolute workspace root.
            file_path: Relative file path to scan.

        Returns:
            List of SecurityFinding.
        """
        import os

        findings: List[SecurityFinding] = []
        abs_path = os.path.join(workspace_path, file_path)
        if not os.path.exists(abs_path):
            return findings

        try:
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for idx, line in enumerate(lines, start=1):
                # 1. SQL Injection check
                if re.search(r"execute\(\s*f['\"]", line):
                    findings.append(
                        SecurityFinding(
                            file_path=file_path,
                            rule_id="SEC-SQL-INJECTION",
                            severity="high",
                            message="Potential SQL injection detected: formatted string in execute call.",
                            line_number=idx,
                        )
                    )
                # 2. Hardcoded secret pattern
                if re.search(r"(api_key|password|secret|token)\s*=\s*['\"][a-zA-Z0-9_\-]{8,}['\"]", line, re.I):
                    findings.append(
                        SecurityFinding(
                            file_path=file_path,
                            rule_id="SEC-HARDCODED-SECRET",
                            severity="medium",
                            message="Possible hardcoded secret or API key detected.",
                            line_number=idx,
                        )
                    )
                # 3. Dangerous eval() call
                if "eval(" in line and "def eval" not in line:
                    findings.append(
                        SecurityFinding(
                            file_path=file_path,
                            rule_id="SEC-DANGEROUS-EVAL",
                            severity="high",
                            message="Unsafe eval() usage detected.",
                            line_number=idx,
                        )
                    )
        except Exception:
            pass

        return findings
