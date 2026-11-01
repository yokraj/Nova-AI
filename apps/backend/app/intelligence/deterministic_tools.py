"""Deterministic Tools & Safe Execution Module for Nova AI Core Intelligence.

Provides deterministic tools for mathematical computation, safe AST-based arithmetic
evaluation, step-by-step explanations, and isolated code validation.
Deterministic tasks are executed directly with 100% mathematical accuracy without
unnecessary or hallucination-prone LLM calls.
"""

import ast
import operator
import re
import math
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple, Union
import structlog

logger = structlog.get_logger(__name__)

# Supported safe AST binary operators
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


class DeterministicCalculator:
    """Safe, AST-based mathematical evaluator with step-by-step derivation."""

    def __init__(self) -> None:
        logger.info("deterministic_calculator_initialized")

    def _eval_ast_node(self, node: ast.AST) -> Union[int, float]:
        """Recursively evaluates safe AST arithmetic nodes."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value)}")

        if isinstance(node, ast.BinOp):
            left_val = self._eval_ast_node(node.left)
            right_val = self._eval_ast_node(node.right)
            op_type = type(node.op)
            if op_type not in SAFE_OPERATORS:
                raise ValueError(f"Unsupported binary operator: {op_type}")
            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right_val == 0:
                raise ZeroDivisionError("Division by zero in arithmetic expression")
            if op_type == ast.Pow and (abs(left_val) > 10000 or right_val > 100):
                raise ValueError("Exponentiation exceeds safe magnitude threshold")
            return SAFE_OPERATORS[op_type](left_val, right_val)

        if isinstance(node, ast.UnaryOp):
            operand_val = self._eval_ast_node(node.operand)
            op_type = type(node.op)
            if op_type not in SAFE_OPERATORS:
                raise ValueError(f"Unsupported unary operator: {op_type}")
            return SAFE_OPERATORS[op_type](operand_val)

        raise ValueError(f"Unsafe or unsupported AST node: {type(node)}")

    def safe_evaluate_expression(self, expression_str: str) -> Union[int, float]:
        """Safely parses and evaluates mathematical expression string via AST."""
        cleaned = expression_str.strip()
        # Replace common alternative symbols
        cleaned = cleaned.replace("×", "*").replace("÷", "/").replace("^", "**")
        
        tree = ast.parse(cleaned, mode="eval")
        return self._eval_ast_node(tree.body)

    def extract_and_evaluate(self, text: str) -> Optional[Dict[str, Any]]:
        """Detects arithmetic requests in natural language, extracts operands, and computes exact solution."""
        cleaned = text.strip()

        # Pattern 1: Explicit word patterns (e.g. "What is 19 multiplied by 37?", "multiply 19 and 37", "19 times 37")
        mult_match = re.search(
            r"(?:what\s+is\s+|calculate\s+|compute\s+)?(\d+(?:\.\d+)?)\s*(?:multiplied\s+by|times|\*|x)\s*(\d+(?:\.\d+)?)",
            cleaned,
            re.IGNORECASE,
        )
        if mult_match:
            a = float(mult_match.group(1)) if "." in mult_match.group(1) else int(mult_match.group(1))
            b = float(mult_match.group(2)) if "." in mult_match.group(2) else int(mult_match.group(2))
            res = a * b
            explanation = self._generate_multiplication_steps(a, b, res)
            return {
                "operation": "multiplication",
                "operands": [a, b],
                "result": res,
                "expression": f"{a} * {b}",
                "formatted_output": explanation,
                "is_deterministic": True,
            }

        # Pattern 2: Addition (e.g. "What is 45 plus 98?", "add 45 and 98")
        add_match = re.search(
            r"(?:what\s+is\s+|calculate\s+|compute\s+)?(\d+(?:\.\d+)?)\s*(?:plus|\+)\s*(\d+(?:\.\d+)?)",
            cleaned,
            re.IGNORECASE,
        )
        if add_match:
            a = float(add_match.group(1)) if "." in add_match.group(1) else int(add_match.group(1))
            b = float(add_match.group(2)) if "." in add_match.group(2) else int(add_match.group(2))
            res = a + b
            explanation = (
                f"**Result**: {res}\n\n"
                f"**Step-by-Step Explanation**:\n"
                f"1. Problem: Add {a} and {b}.\n"
                f"2. {a} + {b} = {res}."
            )
            return {
                "operation": "addition",
                "operands": [a, b],
                "result": res,
                "expression": f"{a} + {b}",
                "formatted_output": explanation,
                "is_deterministic": True,
            }

        # Pattern 3: Subtraction (e.g. "What is 100 minus 37?", "subtract 37 from 100")
        sub_match = re.search(
            r"(?:what\s+is\s+|calculate\s+|compute\s+)?(\d+(?:\.\d+)?)\s*(?:minus|\-)\s*(\d+(?:\.\d+)?)",
            cleaned,
            re.IGNORECASE,
        )
        if sub_match:
            a = float(sub_match.group(1)) if "." in sub_match.group(1) else int(sub_match.group(1))
            b = float(sub_match.group(2)) if "." in sub_match.group(2) else int(sub_match.group(2))
            res = a - b
            explanation = (
                f"**Result**: {res}\n\n"
                f"**Step-by-Step Explanation**:\n"
                f"1. Problem: Subtract {b} from {a}.\n"
                f"2. {a} - {b} = {res}."
            )
            return {
                "operation": "subtraction",
                "operands": [a, b],
                "result": res,
                "expression": f"{a} - {b}",
                "formatted_output": explanation,
                "is_deterministic": True,
            }

        # Pattern 4: Division (e.g. "What is 144 divided by 12?", "144 / 12")
        div_match = re.search(
            r"(?:what\s+is\s+|calculate\s+|compute\s+)?(\d+(?:\.\d+)?)\s*(?:divided\s+by|\/)\s*(\d+(?:\.\d+)?)",
            cleaned,
            re.IGNORECASE,
        )
        if div_match:
            a = float(div_match.group(1)) if "." in div_match.group(1) else int(div_match.group(1))
            b = float(div_match.group(2)) if "." in div_match.group(2) else int(div_match.group(2))
            if b == 0:
                return {
                    "operation": "division",
                    "error": "Division by zero is undefined.",
                    "is_deterministic": True,
                    "formatted_output": "**Error**: Division by zero is undefined.",
                }
            res = round(a / b, 6)
            if res.is_integer():
                res = int(res)
            explanation = (
                f"**Result**: {res}\n\n"
                f"**Step-by-Step Explanation**:\n"
                f"1. Problem: Divide {a} by {b}.\n"
                f"2. {a} / {b} = {res}."
            )
            return {
                "operation": "division",
                "operands": [a, b],
                "result": res,
                "expression": f"{a} / {b}",
                "formatted_output": explanation,
                "is_deterministic": True,
            }

        # Pattern 5: Raw mathematical expression (e.g. "19 * 37", "(14 + 6) * 3", "2 ** 8")
        expr_cand = re.sub(r"^(?:calculate|compute|what\s+is|evaluate)\s+", "", cleaned, flags=re.IGNORECASE).strip()
        expr_cand = expr_cand.rstrip("?").strip()
        if re.match(r"^[\d\.\s\+\-\*\/\(\)\^\%]+$", expr_cand) and any(op in expr_cand for op in "+-*/^%"):
            try:
                res = self.safe_evaluate_expression(expr_cand)
                if isinstance(res, float) and res.is_integer():
                    res = int(res)
                explanation = (
                    f"**Result**: {res}\n\n"
                    f"**Evaluation**:\n"
                    f"Expression: `{expr_cand}` = **{res}**"
                )
                return {
                    "operation": "expression",
                    "expression": expr_cand,
                    "result": res,
                    "formatted_output": explanation,
                    "is_deterministic": True,
                }
            except Exception:
                pass

        return None

    def _generate_multiplication_steps(
        self, a: Union[int, float], b: Union[int, float], result: Union[int, float]
    ) -> str:
        """Constructs clear, rigorous step-by-step arithmetic explanation."""
        if isinstance(a, int) and isinstance(b, int) and b >= 10:
            tens = (b // 10) * 10
            units = b % 10
            p1 = a * tens
            p2 = a * units
            return (
                f"**Result**: {result}\n\n"
                f"**Step-by-Step Explanation**:\n"
                f"1. Break down the multiplier {b} into place values: `{b} = {tens} + {units}`.\n"
                f"2. Multiply {a} by the tens place ({tens}):\n"
                f"   `{a} × {tens} = {p1}`\n"
                f"3. Multiply {a} by the units place ({units}):\n"
                f"   `{a} × {units} = {p2}`\n"
                f"4. Add the two partial products together:\n"
                f"   `{p1} + {p2} = {result}`\n\n"
                f"Therefore, **{a} × {b} = {result}**."
            )

        return (
            f"**Result**: {result}\n\n"
            f"**Step-by-Step Explanation**:\n"
            f"1. Multiply `{a}` by `{b}`.\n"
            f"2. `{a} × {b} = {result}`."
        )


class SafeCodeValidator:
    """Validates Python code syntax and safe execution bounds."""

    def __init__(self) -> None:
        logger.info("safe_code_validator_initialized")

    def validate_syntax(self, code_str: str) -> Dict[str, Any]:
        """Parses Python source code with ast to detect syntax errors before presentation."""
        try:
            ast.parse(code_str)
            return {"valid": True, "error": None}
        except SyntaxError as syn_err:
            return {
                "valid": False,
                "error": f"SyntaxError at line {syn_err.lineno}: {syn_err.msg}",
                "lineno": syn_err.lineno,
            }

    def execute_safely(self, code_str: str, timeout_seconds: float = 2.0) -> Dict[str, Any]:
        """Executes Python code snippet in isolated sub-process with bounded timeout."""
        val = self.validate_syntax(code_str)
        if not val["valid"]:
            return {"success": False, "error": val["error"], "output": ""}

        try:
            res = subprocess.run(
                [sys.executable, "-c", code_str],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            return {
                "success": res.returncode == 0,
                "stdout": res.stdout.strip(),
                "stderr": res.stderr.strip(),
                "returncode": res.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Execution timed out after {timeout_seconds}s limit",
                "stdout": "",
            }
        except Exception as exc:
            return {"success": False, "error": str(exc), "stdout": ""}

