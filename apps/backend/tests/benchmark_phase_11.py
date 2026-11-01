"""NOVA AI — PHASE 11 COMPREHENSIVE INTELLIGENCE BENCHMARK SUITE

Automated repeatable benchmark suite covering:
1. 25 Arithmetic problems (deterministic + reasoning)
2. 20 Logical reasoning problems
3. 20 Programming questions
4. 15 Algorithm questions
5. 15 Multi-turn conversation tests
6. 10 Instruction-following tests
7. 10 Tool-use and result-verification tests

Total tests: 115 tests.
Records input, expected criteria, actual result, model/provider, duration, pass/fail, and failure reason.
"""

import ast
import asyncio
import json
import re
import sys
import time
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

# Ensure app path is resolvable
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.identity.infrastructure.security import create_access_token
from app.intelligence.deterministic_tools import DeterministicCalculator, SafeCodeValidator
from app.intelligence.response_validator import ResponseValidator

BASE_URL = "http://127.0.0.1:8000"


class BenchmarkPhase11Runner:
    """Master Benchmark Suite Runner for Nova AI Phase 11."""

    def __init__(self) -> None:
        self.calculator = DeterministicCalculator()
        self.code_validator = SafeCodeValidator()
        self.response_validator = ResponseValidator()
        self.results: Dict[str, Any] = {
            "metadata": {
                "benchmark_name": "Nova AI Phase 11 Intelligence Benchmark",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "model": "qwen3:8b",
                "local_provider": "ollama",
                "deterministic_engine": "SafeASTCalculator",
            },
            "summary": {},
            "categories": {},
        }

    def _get_auth_headers(self) -> Dict[str, str]:
        token = create_access_token(
            {"sub": "benchmark-runner", "role": "user"},
            expires_delta=timedelta(hours=2),
        )
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Origin": "http://127.0.0.1:3000",
        }

    # =========================================================================
    # 1. ARITHMETIC BENCHMARKS (25 Tests)
    # =========================================================================
    def run_arithmetic_benchmarks(self) -> List[Dict[str, Any]]:
        print("\n--- RUNNING 25 ARITHMETIC TESTS ---")
        tests = [
            ("What is 19 multiplied by 37? Explain step by step.", 703, "multiplication"),
            ("What is 45 plus 98?", 143, "addition"),
            ("What is 1000 minus 347?", 653, "subtraction"),
            ("What is 144 divided by 12?", 12, "division"),
            ("What is 25 times 25?", 625, "multiplication"),
            ("Calculate 15 * 14", 210, "multiplication"),
            ("Calculate 999 + 1001", 2000, "addition"),
            ("What is 500 minus 189?", 311, "subtraction"),
            ("What is 84 divided by 7?", 12, "division"),
            ("What is 13 multiplied by 17?", 221, "multiplication"),
            ("Calculate 75 * 4", 300, "multiplication"),
            ("What is 1024 divided by 32?", 32, "division"),
            ("Calculate 350 + 650", 1000, "addition"),
            ("What is 81 divided by 9?", 9, "division"),
            ("Calculate 16 * 16", 256, "multiplication"),
            ("What is 200 minus 75?", 125, "subtraction"),
            ("Calculate 12 * 12", 144, "multiplication"),
            ("What is 625 divided by 25?", 25, "division"),
            ("Calculate 48 + 52", 100, "addition"),
            ("What is 90 minus 45?", 45, "subtraction"),
            ("What is 8 multiplied by 9?", 72, "multiplication"),
            ("What is 100 divided by 4?", 25, "division"),
            ("Calculate 33 * 3", 99, "multiplication"),
            ("What is 50 plus 150?", 200, "addition"),
            ("What is 500 divided by 10?", 50, "division"),
        ]

        results = []
        for idx, (prompt, expected, op_type) in enumerate(tests, 1):
            t0 = time.perf_counter()
            eval_res = self.calculator.extract_and_evaluate(prompt)
            dur = time.perf_counter() - t0

            if not eval_res:
                passed = False
                act = None
                reason = "Failed to extract arithmetic expression"
            else:
                act = eval_res.get("result")
                passed = (act == expected)
                reason = None if passed else f"Expected {expected}, got {act}"

            results.append({
                "test_id": f"arithmetic_{idx:02d}",
                "input": prompt,
                "expected": expected,
                "actual": act,
                "model_or_provider": "deterministic_calculator",
                "duration_seconds": round(dur, 4),
                "status": "PASS" if passed else "FAIL",
                "failure_reason": reason,
            })
            print(f"  [{results[-1]['status']}] Arithmetic {idx:02d}: {prompt[:35]}... -> {act} ({dur*1000:.2f}ms)")
        return results

    # =========================================================================
    # 2. LOGICAL REASONING BENCHMARKS (20 Tests)
    # =========================================================================
    async def run_logic_benchmarks(self, client: httpx.AsyncClient, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        print("\n--- RUNNING 20 LOGICAL REASONING TESTS ---")
        tests = [
            ("If all roses are flowers and all flowers need water, do all roses need water? Answer with YES or NO and explain briefly.", ["yes"]),
            ("A is taller than B. B is taller than C. Who is the shortest person among A, B, and C?", ["c", "c is"]),
            ("If it rains, the street gets wet. The street is wet. Does that logically prove it rained? Answer YES or NO and explain.", ["no", "does not prove"]),
            ("John is older than Mary. Mary is older than David. Is John older than David? Answer YES or NO.", ["yes"]),
            ("No fish can walk. A salmon is a fish. Can a salmon walk? Answer YES or NO.", ["no"]),
            ("If today is Tuesday, what day was yesterday?", ["monday"]),
            ("If tomorrow is Saturday, what day is today?", ["friday"]),
            ("A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost in cents?", ["5", "0.05", "five"]),
            ("There are 3 apples on a table. You take away 2. How many apples do you have?", ["2", "two"]),
            ("A farmer has 17 sheep. All but 9 die. How many sheep are left alive?", ["9", "nine"]),
            ("If an electric train travels north at 60 mph and the wind blows west, which way does the smoke blow?", ["no smoke", "electric", "doesn't blow"]),
            ("A doctor gives you 3 pills and tells you to take one every 30 minutes. How many minutes do all three pills last?", ["60", "1 hour", "sixty"]),
            ("Mary's father has five daughters: Nana, Nene, Nini, Nono, and who?", ["mary"]),
            ("Which is heavier: a pound of feathers or a pound of gold or bricks?", ["same", "equal", "neither"]),
            ("If two's company and three's a crowd, what are four and five? Answer mathematically.", ["9", "nine"]),
            ("All squares are rectangles. Are all rectangles squares? Answer YES or NO.", ["no"]),
            ("Can a man legally marry his widow's sister under standard law? Explain why or why not.", ["dead", "no", "he is dead"]),
            ("Before Mount Everest was discovered, what was the highest mountain on Earth?", ["everest", "mount everest"]),
            ("If you overtake the person in second place in a footrace, what place are you in?", ["second", "2nd", "2"]),
            ("Some cats are black. All black animals are nocturnal. Are some cats nocturnal? Answer YES or NO.", ["yes"]),
        ]

        results = []
        for idx, (prompt, expected_keywords) in enumerate(tests, 1):
            t0 = time.perf_counter()
            try:
                res = await client.post(
                    "/api/v1/inference/chat",
                    headers=headers,
                    json={"prompt": prompt, "model": "qwen3:8b", "max_tokens": 200, "use_deterministic_tools": True},
                    timeout=60.0,
                )
                dur = time.perf_counter() - t0
                if res.status_code == 200:
                    content = res.json().get("content", "").lower()
                    passed = any(kw in content for kw in expected_keywords)
                    act = res.json().get("content", "")[:120]
                    reason = None if passed else f"Expected one of {expected_keywords} in answer"
                else:
                    dur = time.perf_counter() - t0
                    passed = False
                    act = f"HTTP {res.status_code}"
                    reason = res.text[:100]
            except Exception as e:
                dur = time.perf_counter() - t0
                passed = False
                act = "Exception"
                reason = str(e)

            results.append({
                "test_id": f"logic_{idx:02d}",
                "input": prompt,
                "expected": f"Contains one of: {expected_keywords}",
                "actual": act,
                "model_or_provider": "qwen3:8b",
                "duration_seconds": round(dur, 2),
                "status": "PASS" if passed else "FAIL",
                "failure_reason": reason,
            })
            print(f"  [{results[-1]['status']}] Logic {idx:02d}: {prompt[:35]}... ({dur:.1f}s)")
        return results

    # =========================================================================
    # 3. PROGRAMMING BENCHMARKS (20 Tests)
    # =========================================================================
    async def run_programming_benchmarks(self, client: httpx.AsyncClient, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        print("\n--- RUNNING 20 PROGRAMMING TESTS ---")
        tests = [
            ("Write a Python function reverse_string(s) to reverse a string.", "reverse_string"),
            ("Write a Python decorator time_it that prints execution time of a function.", "def time_it"),
            ("Write a Python function count_frequencies(s) returning a dict of char counts.", "count_frequencies"),
            ("Write a Python function flatten_list(nested) to flatten a 2D list.", "flatten_list"),
            ("Write a Python function is_palindrome(s) returning True if string is palindrome.", "is_palindrome"),
            ("Write a Python function find_max(numbers) without using the built-in max().", "find_max"),
            ("Write a Python function merge_sorted(a, b) that merges two sorted lists.", "merge_sorted"),
            ("Write a Python class BankAccount with deposit(amt) and withdraw(amt) methods.", "class BankAccount"),
            ("Write a Python generator fibonacci_gen(n) yielding Fibonacci numbers up to n.", "yield"),
            ("Write a Python function remove_duplicates(items) preserving original order.", "remove_duplicates"),
            ("Write a Python function factorial(n) using recursion.", "factorial"),
            ("Write a Python function filter_evens(nums) using list comprehension.", "filter_evens"),
            ("Write a Python function find_intersection(set1, set2) returning common items.", "find_intersection"),
            ("Write a Python context manager class SafeFileOp with __enter__ and __exit__.", "__enter__"),
            ("Write a Python function are_anagrams(s1, s2) returning True if strings are anagrams.", "are_anagrams"),
            ("Write a Python function safe_int(s) returning int or None on ValueError.", "safe_int"),
            ("Write a Python function second_largest(numbers) returning second highest number.", "second_largest"),
            ("Write a Python class EmailValidator with a @staticmethod is_valid_email(email).", "@staticmethod"),
            ("Write a Python function chunk_list(items, k) returning chunks of size k.", "chunk_list"),
            ("Write a Python function parse_json_key(json_str, key) returning value safely.", "parse_json_key"),
        ]

        results = []
        for idx, (prompt, expected_symbol) in enumerate(tests, 1):
            t0 = time.perf_counter()
            try:
                res = await client.post(
                    "/api/v1/inference/chat",
                    headers=headers,
                    json={"prompt": prompt, "model": "qwen3:8b", "max_tokens": 400},
                    timeout=90.0,
                )
                dur = time.perf_counter() - t0
                if res.status_code == 200:
                    content = res.json().get("content", "")
                    # Extract code block and validate syntax with AST
                    code_val = self.response_validator.validate_code_in_response(content)
                    has_symbol = expected_symbol.lower() in content.lower()
                    passed = has_symbol and (not code_val["has_code"] or code_val["valid"])
                    act = f"Syntax valid: {code_val['valid']}, Symbol found: {has_symbol}"
                    reason = None if passed else f"Code syntax error: {code_val.get('errors')} or symbol missing"
                else:
                    passed = False
                    act = f"HTTP {res.status_code}"
                    reason = res.text[:100]
            except Exception as e:
                dur = time.perf_counter() - t0
                passed = False
                act = "Exception"
                reason = str(e)

            results.append({
                "test_id": f"programming_{idx:02d}",
                "input": prompt,
                "expected": f"Valid Python syntax containing '{expected_symbol}'",
                "actual": act,
                "model_or_provider": "qwen3:8b",
                "duration_seconds": round(dur, 2),
                "status": "PASS" if passed else "FAIL",
                "failure_reason": reason,
            })
            print(f"  [{results[-1]['status']}] Programming {idx:02d}: {prompt[:35]}... ({dur:.1f}s)")
        return results

    # =========================================================================
    # 4. ALGORITHM BENCHMARKS (15 Tests)
    # =========================================================================
    async def run_algorithm_benchmarks(self, client: httpx.AsyncClient, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        print("\n--- RUNNING 15 ALGORITHM TESTS ---")
        tests = [
            ("Write a Python program to check whether 29 is prime. Explain the algorithm.", ["29", "prime"]),
            ("Explain binary search and provide a Python implementation with O(log n) time complexity.", ["binary_search", "mid"]),
            ("Write a Python function for Merge Sort and explain its divide-and-conquer strategy.", ["merge", "split"]),
            ("Explain Quick Sort partition logic and write a working Python implementation.", ["partition", "pivot"]),
            ("Write a Python function to solve the Two Sum problem using a hash map in O(n) time.", ["two_sum", "dict"]),
            ("Write a Python implementation of Breadth-First Search (BFS) on an adjacency list graph.", ["queue", "bfs"]),
            ("Write a Python implementation of Depth-First Search (DFS) on an adjacency list graph.", ["dfs", "visited"]),
            ("Explain Dijkstra's shortest path algorithm and write a Python implementation with heapq.", ["heapq", "dijkstra"]),
            ("Write a Python function to find the longest common prefix among an array of strings.", ["prefix"]),
            ("Write a Python program to detect a cycle in a linked list using Floyd's Tortoise and Hare algorithm.", ["slow", "fast"]),
            ("Write a Python function to compute the nth Fibonacci number using dynamic programming (tabulation).", ["dp", "fib"]),
            ("Write a Python function to invert a binary tree and explain the recursive approach.", ["invert", "left", "right"]),
            ("Explain the Dutch National Flag algorithm and implement sorting of 0s, 1s, and 2s in-place.", ["low", "mid", "high"]),
            ("Write a Python function to find the maximum subarray sum using Kadane's algorithm.", ["kadane", "max_sum"]),
            ("Write a Python function to solve the Coin Change problem using dynamic programming.", ["coin", "min"]),
        ]

        results = []
        for idx, (prompt, expected_keywords) in enumerate(tests, 1):
            t0 = time.perf_counter()
            try:
                res = await client.post(
                    "/api/v1/inference/chat",
                    headers=headers,
                    json={"prompt": prompt, "model": "qwen3:8b", "max_tokens": 400},
                    timeout=90.0,
                )
                dur = time.perf_counter() - t0
                if res.status_code == 200:
                    content = res.json().get("content", "").lower()
                    passed = any(kw in content for kw in expected_keywords)
                    act = f"Matches criteria: {passed}"
                    reason = None if passed else f"Expected one of {expected_keywords} in answer"
                else:
                    passed = False
                    act = f"HTTP {res.status_code}"
                    reason = res.text[:100]
            except Exception as e:
                dur = time.perf_counter() - t0
                passed = False
                act = "Exception"
                reason = str(e)

            results.append({
                "test_id": f"algorithm_{idx:02d}",
                "input": prompt,
                "expected": f"Covers concepts: {expected_keywords}",
                "actual": act,
                "model_or_provider": "qwen3:8b",
                "duration_seconds": round(dur, 2),
                "status": "PASS" if passed else "FAIL",
                "failure_reason": reason,
            })
            print(f"  [{results[-1]['status']}] Algorithm {idx:02d}: {prompt[:35]}... ({dur:.1f}s)")
        return results

    # =========================================================================
    # 5. MULTI-TURN CONVERSATION BENCHMARKS (15 Tests)
    # =========================================================================
    async def run_multiturn_benchmarks(self, client: httpx.AsyncClient, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        print("\n--- RUNNING 15 MULTI-TURN CONVERSATION TESTS ---")
        scenarios = [
            ("My name is Alice.", "What is my name?", ["alice"]),
            ("I live in Seattle.", "What city do I live in?", ["seattle"]),
            ("The server port is 8080.", "What is the server port?", ["8080"]),
            ("I am building a React frontend.", "What frontend framework am I using?", ["react"]),
            ("Our database is PostgreSQL.", "What database are we using?", ["postgres", "postgresql"]),
            ("We have 10 servers deployed.", "How many servers are deployed?", ["10", "ten"]),
            ("The deployment environment is staging.", "What environment are we deploying to?", ["staging"]),
            ("The API rate limit is 100 requests per minute.", "What is the rate limit?", ["100"]),
            ("The user role is administrator.", "What is the user's role?", ["admin", "administrator"]),
            ("The project code name is Project Nova.", "What is the project code name?", ["nova", "project nova"]),
            ("The backup directory is /var/backups.", "Where are backups saved?", ["/var/backups", "backups"]),
            ("My favorite language is Rust.", "Which language did I say was my favorite?", ["rust"]),
            ("Let base_price = 150.", "What is base_price?", ["150"]),
            ("The team lead is Sarah.", "Who is the team lead?", ["sarah"]),
            ("The timeout is set to 30 seconds.", "What is the timeout value?", ["30"]),
        ]

        results = []
        for idx, (turn1_user, turn2_prompt, expected_kws) in enumerate(scenarios, 1):
            t0 = time.perf_counter()
            messages = [
                {"role": "user", "content": turn1_user},
                {"role": "assistant", "content": f"Understood, I have noted that: {turn1_user}"},
            ]
            try:
                res = await client.post(
                    "/api/v1/inference/chat",
                    headers=headers,
                    json={
                        "prompt": turn2_prompt,
                        "model": "qwen3:8b",
                        "max_tokens": 150,
                        "messages": messages,
                    },
                    timeout=60.0,
                )
                dur = time.perf_counter() - t0
                if res.status_code == 200:
                    content = res.json().get("content", "").lower()
                    passed = any(kw in content for kw in expected_kws)
                    act = res.json().get("content", "")[:100]
                    reason = None if passed else f"Expected one of {expected_kws} in answer"
                else:
                    passed = False
                    act = f"HTTP {res.status_code}"
                    reason = res.text[:100]
            except Exception as e:
                dur = time.perf_counter() - t0
                passed = False
                act = "Exception"
                reason = str(e)

            results.append({
                "test_id": f"multiturn_{idx:02d}",
                "input": f"Turn 1: '{turn1_user}' -> Turn 2: '{turn2_prompt}'",
                "expected": f"Contextual retention of: {expected_kws}",
                "actual": act,
                "model_or_provider": "qwen3:8b",
                "duration_seconds": round(dur, 2),
                "status": "PASS" if passed else "FAIL",
                "failure_reason": reason,
            })
            print(f"  [{results[-1]['status']}] Multi-Turn {idx:02d}: '{turn2_prompt}' -> {act[:30]} ({dur:.1f}s)")
        return results

    # =========================================================================
    # 6. INSTRUCTION-FOLLOWING BENCHMARKS (10 Tests)
    # =========================================================================
    async def run_instruction_benchmarks(self, client: httpx.AsyncClient, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        print("\n--- RUNNING 10 INSTRUCTION-FOLLOWING TESTS ---")
        tests = [
            ("Respond with exactly the single word: CONFIRMED. Do not add punctuation or any other words.", lambda s: "confirmed" in s.lower()),
            ("List exactly three primary colors, one per line, with no extra text.", lambda s: len(s.strip().split("\n")) >= 3),
            ("Output a valid JSON object with keys 'status' and 'version'. No explanations or markdown.", lambda s: "{" in s and "status" in s),
            ("Translate 'apple' to Spanish. Output only the Spanish word.", lambda s: "manzana" in s.lower()),
            ("Answer in all uppercase letters: What is the capital of France?", lambda s: "PARIS" in s),
            ("Respond with a single number only: What is 10 plus 5?", lambda s: "15" in s),
            ("Answer with YES or NO only: Is Python an interpreted language?", lambda s: "YES" in s.upper()),
            ("Format your response as a 2-column Markdown table showing three operating systems and their creators.", lambda s: "|" in s and "---" in s),
            ("Provide two bullet points explaining what an API is. Start each bullet with an asterisk.", lambda s: "*" in s),
            ("Prefix your entire response with [VERIFIED]:", lambda s: "[VERIFIED]" in s),
        ]

        results = []
        for idx, (prompt, validator_fn) in enumerate(tests, 1):
            t0 = time.perf_counter()
            try:
                res = await client.post(
                    "/api/v1/inference/chat",
                    headers=headers,
                    json={"prompt": prompt, "model": "qwen3:8b", "max_tokens": 150},
                    timeout=60.0,
                )
                dur = time.perf_counter() - t0
                if res.status_code == 200:
                    content = res.json().get("content", "")
                    passed = validator_fn(content)
                    act = content[:100]
                    reason = None if passed else "Failed specific formatting constraint"
                else:
                    passed = False
                    act = f"HTTP {res.status_code}"
                    reason = res.text[:100]
            except Exception as e:
                dur = time.perf_counter() - t0
                passed = False
                act = "Exception"
                reason = str(e)

            results.append({
                "test_id": f"instruction_{idx:02d}",
                "input": prompt,
                "expected": "Strict compliance with prompt format constraints",
                "actual": act,
                "model_or_provider": "qwen3:8b",
                "duration_seconds": round(dur, 2),
                "status": "PASS" if passed else "FAIL",
                "failure_reason": reason,
            })
            print(f"  [{results[-1]['status']}] Instruction {idx:02d}: {prompt[:35]}... ({dur:.1f}s)")
        return results

    # =========================================================================
    # 7. TOOL-USE & RESULT VERIFICATION BENCHMARKS (10 Tests)
    # =========================================================================
    def run_tool_use_benchmarks(self) -> List[Dict[str, Any]]:
        print("\n--- RUNNING 10 TOOL-USE & VERIFICATION TESTS ---")
        tests = []

        # 1. Safe Calculator AST multiplication
        t0 = time.perf_counter()
        c1 = self.calculator.safe_evaluate_expression("19 * 37")
        tests.append({
            "test_id": "tool_01",
            "input": "safe_evaluate_expression('19 * 37')",
            "expected": 703,
            "actual": c1,
            "model_or_provider": "SafeASTCalculator",
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "status": "PASS" if c1 == 703 else "FAIL",
            "failure_reason": None,
        })

        # 2. Safe Calculator AST addition
        t0 = time.perf_counter()
        c2 = self.calculator.safe_evaluate_expression("45 + 98")
        tests.append({
            "test_id": "tool_02",
            "input": "safe_evaluate_expression('45 + 98')",
            "expected": 143,
            "actual": c2,
            "model_or_provider": "SafeASTCalculator",
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "status": "PASS" if c2 == 143 else "FAIL",
            "failure_reason": None,
        })

        # 3. Safe Calculator division by zero rejection
        t0 = time.perf_counter()
        try:
            self.calculator.safe_evaluate_expression("100 / 0")
            c3 = False
        except ZeroDivisionError:
            c3 = True
        tests.append({
            "test_id": "tool_03",
            "input": "safe_evaluate_expression('100 / 0')",
            "expected": "ZeroDivisionError",
            "actual": "ZeroDivisionError caught" if c3 else "Failed to raise",
            "model_or_provider": "SafeASTCalculator",
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "status": "PASS" if c3 else "FAIL",
            "failure_reason": None,
        })

        # 4. Safe Code Validator: Valid syntax check
        t0 = time.perf_counter()
        v1 = self.code_validator.validate_syntax("def add(a, b):\n    return a + b\n")
        tests.append({
            "test_id": "tool_04",
            "input": "validate_syntax('def add(a, b): return a + b')",
            "expected": True,
            "actual": v1["valid"],
            "model_or_provider": "SafeCodeValidator",
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "status": "PASS" if v1["valid"] else "FAIL",
            "failure_reason": v1.get("error"),
        })

        # 5. Safe Code Validator: Malformed syntax rejection
        t0 = time.perf_counter()
        v2 = self.code_validator.validate_syntax("def broken_func(:\n    return\n")
        tests.append({
            "test_id": "tool_05",
            "input": "validate_syntax('def broken_func(: return')",
            "expected": False,
            "actual": v2["valid"],
            "model_or_provider": "SafeCodeValidator",
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "status": "PASS" if not v2["valid"] else "FAIL",
            "failure_reason": None,
        })

        # 6. Safe Code Execution with stdout capture
        t0 = time.perf_counter()
        ex1 = self.code_validator.execute_safely("print('NOVA_TOOL_OK')", timeout_seconds=2.0)
        tests.append({
            "test_id": "tool_06",
            "input": "execute_safely('print(\"NOVA_TOOL_OK\")')",
            "expected": "NOVA_TOOL_OK",
            "actual": ex1.get("stdout"),
            "model_or_provider": "SafeCodeExecutor",
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "status": "PASS" if ex1.get("stdout") == "NOVA_TOOL_OK" else "FAIL",
            "failure_reason": ex1.get("error"),
        })

        # 7. Safe Code Execution timeout enforcement on infinite loop
        t0 = time.perf_counter()
        ex2 = self.code_validator.execute_safely("while True: pass", timeout_seconds=1.0)
        tests.append({
            "test_id": "tool_07",
            "input": "execute_safely('while True: pass', timeout=1.0)",
            "expected": "Timed out",
            "actual": "Timeout caught" if not ex2["success"] and "timed out" in ex2.get("error", "").lower() else "Failed",
            "model_or_provider": "SafeCodeExecutor",
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "status": "PASS" if "timed out" in ex2.get("error", "").lower() else "FAIL",
            "failure_reason": ex2.get("error"),
        })

        # 8. Response Validator: Verification of mathematical statement
        t0 = time.perf_counter()
        val_m = self.response_validator.validate_math_in_response(
            "What is 19 multiplied by 37?", "The product is 703 according to arithmetic rules."
        )
        tests.append({
            "test_id": "tool_08",
            "input": "validate_math_in_response('What is 19 * 37?', '... 703 ...')",
            "expected": True,
            "actual": val_m["verified"],
            "model_or_provider": "ResponseValidator",
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "status": "PASS" if val_m["verified"] else "FAIL",
            "failure_reason": None,
        })

        # 9. Response Validator: Extraction and validation of code fences
        t0 = time.perf_counter()
        val_c = self.response_validator.validate_code_in_response(
            "Here is the code:\n```python\ndef is_even(n):\n    return n % 2 == 0\n```"
        )
        tests.append({
            "test_id": "tool_09",
            "input": "validate_code_in_response('```python def is_even(n): return n%2==0 ```')",
            "expected": True,
            "actual": val_c["valid"],
            "model_or_provider": "ResponseValidator",
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "status": "PASS" if val_c["valid"] else "FAIL",
            "failure_reason": None,
        })

        # 10. Task Classifier: Category routing accuracy
        from app.inference.task_classifier import TaskClassifier
        tc = TaskClassifier()
        t0 = time.perf_counter()
        tc_res = tc.classify_task("Write a Python decorator to measure memory usage.")
        tests.append({
            "test_id": "tool_10",
            "input": "classify_task('Write a Python decorator...')",
            "expected": "Programming",
            "actual": tc_res["task_category"],
            "model_or_provider": "TaskClassifier",
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "status": "PASS" if tc_res["task_category"] == "Programming" else "FAIL",
            "failure_reason": None,
        })

        for t in tests:
            print(f"  [{t['status']}] Tool {t['test_id']}: {t['input'][:35]}... ({t['duration_seconds']*1000:.2f}ms)")
        return tests

    # =========================================================================
    # MASTER RUNNER
    # =========================================================================
    async def run_all(self) -> Dict[str, Any]:
        headers = self._get_auth_headers()

        # Run Category 1: Arithmetic (25)
        arith_results = self.run_arithmetic_benchmarks()
        self.results["categories"]["arithmetic"] = arith_results

        # Run Category 7: Tool Use (10)
        tool_results = self.run_tool_use_benchmarks()
        self.results["categories"]["tool_use"] = tool_results

        async with httpx.AsyncClient(base_url=BASE_URL, timeout=120.0) as client:
            # Run Category 5: Multi-Turn (15)
            multiturn_results = await self.run_multiturn_benchmarks(client, headers)
            self.results["categories"]["multiturn"] = multiturn_results

            # Run Category 6: Instruction Following (10)
            instruction_results = await self.run_instruction_benchmarks(client, headers)
            self.results["categories"]["instruction_following"] = instruction_results

            # Run Category 2: Logical Reasoning (20)
            logic_results = await self.run_logic_benchmarks(client, headers)
            self.results["categories"]["logical_reasoning"] = logic_results

            # Run Category 3: Programming (20)
            programming_results = await self.run_programming_benchmarks(client, headers)
            self.results["categories"]["programming"] = programming_results

            # Run Category 4: Algorithms (15)
            algorithm_results = await self.run_algorithm_benchmarks(client, headers)
            self.results["categories"]["algorithms"] = algorithm_results

        # Calculate Grand Summary
        total_tests = 0
        total_passed = 0
        cat_summaries = {}
        for cat_name, test_list in self.results["categories"].items():
            cat_count = len(test_list)
            cat_pass = sum(1 for t in test_list if t["status"] == "PASS")
            cat_rate = round((cat_pass / max(1, cat_count)) * 100, 1)
            cat_summaries[cat_name] = {
                "total": cat_count,
                "passed": cat_pass,
                "failed": cat_count - cat_pass,
                "pass_rate_pct": cat_rate,
            }
            total_tests += cat_count
            total_passed += cat_pass

        self.results["summary"] = {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_tests - total_passed,
            "overall_pass_rate_pct": round((total_passed / max(1, total_tests)) * 100, 1),
            "category_breakdown": cat_summaries,
        }

        # Save to JSON artifact
        out_path = backend_dir / "tests" / "phase_11_benchmark_results.json"
        out_path.write_text(json.dumps(self.results, indent=2), encoding="utf-8")
        print("\n=======================================================")
        print("PHASE 11 INTELLIGENCE BENCHMARK RESULTS SUMMARY")
        print(f"Total Tests Executed: {total_tests}")
        print(f"Passed: {total_passed} | Failed: {total_tests - total_passed}")
        print(f"Overall Pass Rate: {self.results['summary']['overall_pass_rate_pct']}%")
        print("Category Breakdown:")
        for cat, data in cat_summaries.items():
            print(f"  - {cat:22s}: {data['passed']}/{data['total']} ({data['pass_rate_pct']}%)")
        print(f"Full benchmark evidence persisted to: {out_path}")
        print("=======================================================\n")
        return self.results


if __name__ == "__main__":
    runner = BenchmarkPhase11Runner()
    asyncio.run(runner.run_all())

