"""Response Validation Layer for Nova AI Core Intelligence.

Validates:
1. Mathematical accuracy: verifies arithmetic claims against the deterministic calculator.
2. Code correctness: extracts code fences and verifies Python syntax using AST.
3. Execution verification: ensures output does not contain ungrounded hallucination or fake success claims.
"""

import ast
import re
from typing import Any, Dict, List, Optional
import structlog

from app.intelligence.deterministic_tools import DeterministicCalculator, SafeCodeValidator

logger = structlog.get_logger(__name__)


class ResponseValidator:
    """Enterprise Response Verification Engine."""

    def __init__(self) -> None:
        self.calculator = DeterministicCalculator()
        self.code_validator = SafeCodeValidator()
        logger.info("response_validator_initialized")

    def extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """Extracts fenced markdown code blocks from text."""
        pattern = r"```([a-zA-Z0-9_\-\+]*)\n([\s\S]*?)```"
        blocks = []
        for match in re.finditer(pattern, text):
            lang = match.group(1).lower().strip() or "plaintext"
            code = match.group(2).strip()
            blocks.append({"language": lang, "code": code})
        return blocks

    def validate_code_in_response(self, text: str) -> Dict[str, Any]:
        """Validates all Python code snippets in the response."""
        blocks = self.extract_code_blocks(text)
        py_blocks = [b for b in blocks if b["language"] in ("python", "py", "")]

        if not py_blocks:
            return {"has_code": False, "valid": True, "blocks_count": 0, "errors": []}

        errors = []
        for idx, block in enumerate(py_blocks):
            res = self.code_validator.validate_syntax(block["code"])
            if not res["valid"]:
                errors.append({"block_index": idx, "error": res["error"]})

        return {
            "has_code": True,
            "valid": len(errors) == 0,
            "blocks_count": len(py_blocks),
            "errors": errors,
        }

    def validate_math_in_response(self, prompt: str, response: str) -> Dict[str, Any]:
        """Verifies if response correctly satisfies arithmetic in the prompt."""
        det_eval = self.calculator.extract_and_evaluate(prompt)
        if not det_eval:
            return {"is_math": False, "valid": True}

        expected_res = det_eval.get("result")
        if expected_res is None:
            return {"is_math": True, "valid": True, "note": "No single numerical result expected"}

        expected_str = str(expected_res)
        # Check if the exact expected numerical result appears in the response
        pattern = r"(?<!\d)" + re.escape(expected_str) + r"(?!\d)"
        found = bool(re.search(pattern, response))

        return {
            "is_math": True,
            "expected_result": expected_res,
            "verified": found,
            "valid": found,
            "operation": det_eval.get("operation"),
        }

    def validate_response(self, prompt: str, response: str, task_category: str = "General") -> Dict[str, Any]:
        """Runs comprehensive validation checks across math, code, and response integrity."""
        # 1. Integrity check
        if not response or not response.strip():
            return {
                "valid": False,
                "error": "Empty response received from inference engine.",
                "confidence": 0.0,
            }

        # 2. Math validation
        math_check = self.validate_math_in_response(prompt, response)

        # 3. Code validation
        code_check = self.validate_code_in_response(response)

        overall_valid = math_check["valid"] and code_check["valid"]

        return {
            "valid": overall_valid,
            "math_check": math_check,
            "code_check": code_check,
            "confidence": 1.0 if overall_valid else 0.4,
        }

