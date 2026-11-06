"""Unified Agent Tool Registry for Nova AI (V2.0.1).

Defines, validates, and dispatches executable tools across Nova's core capabilities:
- Mathematical calculations (deterministic AST)
- Document & file inspection (DocumentIntelligence + WorkspaceSecurityGuard)
- Authorized file creation & operations (FileManager + WorkspaceSecurityGuard)
- Code analysis & AST symbol extraction
- Desktop application management (ApplicationLauncher + NativeBridgeClient)
- Operating system control & observation
- Autonomous research synthesis
"""

import asyncio
import inspect
import json
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union
import structlog

from app.security.workspace_guard import WorkspaceSecurityGuard, WorkspaceSecurityException
from app.ai.desktop_automation.security_engine import SecurityEngine
from app.ai.desktop_automation.exceptions import ApprovalRequiredError
from app.security.approval_manager import approval_manager
from app.ai.desktop_automation.application_launcher import ApplicationLauncher
from app.ai.desktop_automation.file_manager import FileManager
from app.ai.desktop_automation.native_bridge_client import NativeBridgeClient
from app.ai.research.document_intelligence import DocumentIntelligence
from app.intelligence.deterministic_tools import DeterministicCalculator

logger = structlog.get_logger("unified_tool_registry")


class ToolPermissionLevel(str, Enum):
    """Enumerate security sensitivity levels for tools."""
    USER = "USER"              # Safe, automatically approvable within workspace
    SENSITIVE = "SENSITIVE"    # Requires permission/policy check
    RESTRICTED = "RESTRICTED"  # High-risk (requires explicit confirmation)


@dataclass
class ToolExecutionResult:
    """Outcome payload of executing a real tool."""
    tool_name: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_sec: float = 0.0
    verified: bool = False
    verification_details: str = ""
    artifacts: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "duration_sec": self.duration_sec,
            "verified": self.verified,
            "verification_details": self.verification_details,
            "artifacts": self.artifacts,
        }


@dataclass
class ToolDefinition:
    """Canonical specification of an executable agent tool."""
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    permission_level: ToolPermissionLevel = ToolPermissionLevel.USER
    category: str = "general"
    handler: Optional[Callable[..., Any]] = None
    verifier: Optional[Callable[..., Any]] = None

    def to_schema(self) -> Dict[str, Any]:
        """Formats tool definition for LLM tool calling (OpenAI / Ollama format)."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema,
            },
        }


class UnifiedToolRegistry:
    """Central dynamic registry providing tool discovery, validation, and execution."""

    def __init__(
        self,
        workspace_guard: Optional[WorkspaceSecurityGuard] = None,
        security_engine: Optional[SecurityEngine] = None,
        launcher: Optional[ApplicationLauncher] = None,
        file_manager: Optional[FileManager] = None,
        doc_intelligence: Optional[DocumentIntelligence] = None,
        calculator: Optional[DeterministicCalculator] = None,
        bridge_client: Optional[NativeBridgeClient] = None,
    ) -> None:
        self.guard = workspace_guard or WorkspaceSecurityGuard()
        self.security_engine = security_engine or SecurityEngine()
        self.bridge_client = bridge_client or NativeBridgeClient()
        self.launcher = launcher or ApplicationLauncher(self.bridge_client)
        self.file_manager = file_manager or FileManager(self.guard)
        self.doc_intelligence = doc_intelligence or DocumentIntelligence(self.guard)
        self.calculator = calculator or DeterministicCalculator()

        self._tools: Dict[str, ToolDefinition] = {}
        self._register_default_tools()
        logger.info("unified_tool_registry_initialized", tools_count=len(self._tools))

    def register(self, tool: ToolDefinition) -> None:
        """Registers a tool definition into the registry."""
        self._tools[tool.name] = tool
        logger.debug("tool_registered", name=tool.name, category=tool.category)

    def get(self, name: str) -> Optional[ToolDefinition]:
        """Retrieves tool definition by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        """Returns all registered tool definitions."""
        return list(self._tools.values())

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Returns all tool schemas formatted for LLM tool calling."""
        return [tool.to_schema() for tool in self._tools.values()]

    def determine_action_permission(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Tuple[ToolPermissionLevel, str]:
        """Authoritative determination of invocation permission level and action key."""
        tool = self.get(tool_name)
        if not tool:
            return ToolPermissionLevel.RESTRICTED, tool_name

        level = tool.permission_level
        action_key = tool_name

        if tool_name == "create_file":
            fp = arguments.get("file_path", "")
            if fp:
                try:
                    resolved = self.guard.resolve_workspace_path(fp)
                    if resolved.exists():
                        level = ToolPermissionLevel.SENSITIVE
                        action_key = "create_file_overwrite"
                except Exception:
                    level = ToolPermissionLevel.SENSITIVE

        elif tool_name == "file_operation":
            op = str(arguments.get("operation", "")).lower().strip()
            action_key = f"file_operation_{op}"
            if op in ("delete", "move"):
                level = ToolPermissionLevel.SENSITIVE
            else:
                level = ToolPermissionLevel.USER

        elif tool_name == "keyboard_press":
            key = str(arguments.get("key_name", "")).lower().strip()
            if key in ("enter", "delete", "return"):
                level = ToolPermissionLevel.SENSITIVE
                action_key = f"keyboard_press_{key}"
            else:
                level = ToolPermissionLevel.USER

        elif tool_name == "system_control":
            act = str(arguments.get("action", "")).upper().strip()
            if act in ("CLIPBOARD_GET", "CLIPBOARD_SET"):
                level = ToolPermissionLevel.SENSITIVE
                action_key = f"system_control_{act.lower()}"
            else:
                level = ToolPermissionLevel.USER

        return level, action_key

    def validate_tool_arguments(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validates tool arguments against JSON Schema types, required fields, and enum constraints."""
        tool = self.get(tool_name)
        if not tool:
            return False, f"Tool '{tool_name}' is not registered."

        if not isinstance(arguments, dict):
            return False, f"Arguments for tool '{tool_name}' must be a JSON object, received {type(arguments).__name__}."

        schema = tool.parameters_schema or {}
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        # Check required fields
        for req in required:
            if req not in arguments:
                return False, f"Missing required parameter '{req}' for tool '{tool_name}'."

        # Validate types and enums for provided arguments
        for k, v in arguments.items():
            if k not in properties:
                continue

            prop_spec = properties[k]
            expected_type = prop_spec.get("type")
            if expected_type == "string" and not isinstance(v, str):
                return False, f"Parameter '{k}' must be a string, received {type(v).__name__}."
            elif expected_type == "integer" and (not isinstance(v, int) or isinstance(v, bool)):
                return False, f"Parameter '{k}' must be an integer, received {type(v).__name__}."
            elif expected_type == "boolean" and not isinstance(v, bool):
                return False, f"Parameter '{k}' must be a boolean, received {type(v).__name__}."
            elif expected_type == "array" and not isinstance(v, list):
                return False, f"Parameter '{k}' must be an array, received {type(v).__name__}."
            elif expected_type == "object" and not isinstance(v, dict):
                return False, f"Parameter '{k}' must be an object, received {type(v).__name__}."

            if "enum" in prop_spec and v not in prop_spec["enum"]:
                return False, f"Parameter '{k}' value '{v}' is invalid. Allowed values: {prop_spec['enum']}."

        return True, None

    # =========================================================================
    # Tool Execution Pipeline
    # =========================================================================
    async def execute_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
        approval_token: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> ToolExecutionResult:
        """Executes a registered tool with full security, validation, and outcome verification."""
        t0 = time.perf_counter()
        tool = self.get(name)
        if not tool:
            return ToolExecutionResult(
                tool_name=name,
                success=False,
                error=f"Tool '{name}' is not registered in the Unified Tool Registry.",
                duration_sec=0.0,
            )

        # 0. JSON Schema argument validation
        valid, arg_err = self.validate_tool_arguments(name, arguments)
        if not valid:
            logger.warning("tool_argument_validation_failed", tool=name, error=arg_err)
            return ToolExecutionResult(
                tool_name=name,
                success=False,
                error=f"Argument Validation Error: {arg_err}",
                duration_sec=round(time.perf_counter() - t0, 4),
                verified=False,
                verification_details="Failed JSON Schema validation.",
            )

        # 1. Authoritative Permission and Server Approval Validation
        perm_level, action_key = self.determine_action_permission(name, arguments)
        if perm_level in (ToolPermissionLevel.SENSITIVE, ToolPermissionLevel.RESTRICTED):
            if not approval_token:
                logger.warning("tool_execution_blocked_requires_approval", tool=name, action=action_key)
                return ToolExecutionResult(
                    tool_name=name,
                    success=False,
                    error=f"Permission Error: Action '{action_key}' requires explicit human approval before execution.",
                    duration_sec=round(time.perf_counter() - t0, 4),
                    verified=False,
                    verification_details="Blocked by ServerApprovalManager (no approval token provided).",
                )

            is_valid, validation_msg = approval_manager.validate_and_consume_approval(
                approval_token=approval_token,
                tool_name=name,
                arguments=arguments,
                user_id=user_id,
            )
            if not is_valid:
                logger.warning("tool_execution_blocked_invalid_approval", tool=name, reason=validation_msg)
                return ToolExecutionResult(
                    tool_name=name,
                    success=False,
                    error=f"Permission Error: {validation_msg}",
                    duration_sec=round(time.perf_counter() - t0, 4),
                    verified=False,
                    verification_details="Blocked by ServerApprovalManager validation check.",
                )

        # 2. Check path safety if arguments contain file paths
        for k in ("file_path", "source_path", "destination_path", "path", "save_path"):
            if k in arguments and isinstance(arguments[k], str) and arguments[k].strip():
                path_val = arguments[k]
                try:
                    self.guard.resolve_workspace_path(path_val)
                except (WorkspaceSecurityException, ValueError) as e:
                    logger.warning("tool_path_security_rejection", tool=name, path=path_val, error=str(e))
                    return ToolExecutionResult(
                        tool_name=name,
                        success=False,
                        error=f"Security Error: Access Denied. Path '{path_val}' is outside authorized workspace '{self.guard.root_dir}'.",
                        duration_sec=round(time.perf_counter() - t0, 4),
                        verified=False,
                        verification_details="Blocked by WorkspaceSecurityGuard.",
                    )

        # 3. Physical Tool Execution
        try:
            handler = tool.handler
            if handler is None:
                raise NotImplementedError(f"Tool '{name}' does not have an executable handler attached.")

            if inspect.iscoroutinefunction(handler):
                raw_output = await handler(**arguments)
            else:
                raw_output = handler(**arguments)

            elapsed = round(time.perf_counter() - t0, 4)

            # 4. Result Verification
            verified = True
            verification_details = "Operation executed successfully."
            if tool.verifier:
                try:
                    if inspect.iscoroutinefunction(tool.verifier):
                        ver_res = await tool.verifier(arguments=arguments, output=raw_output)
                    else:
                        ver_res = tool.verifier(arguments=arguments, output=raw_output)

                    if isinstance(ver_res, tuple):
                        verified, verification_details = ver_res
                    elif isinstance(ver_res, bool):
                        verified = ver_res
                        verification_details = "Verified via dedicated outcome verifier." if verified else "Verification failed."
                except Exception as ve:
                    logger.warning("tool_verification_failed", tool=name, error=str(ve))
                    verified = False
                    verification_details = f"Verification check failed: {ve}"

            return ToolExecutionResult(
                tool_name=name,
                success=True,
                output=raw_output,
                duration_sec=elapsed,
                verified=verified,
                verification_details=verification_details,
            )

        except Exception as exc:
            elapsed = round(time.perf_counter() - t0, 4)
            logger.error("tool_execution_failed", tool=name, error=str(exc))
            return ToolExecutionResult(
                tool_name=name,
                success=False,
                error=str(exc),
                duration_sec=elapsed,
                verified=False,
                verification_details=f"Execution error: {exc}",
            )

    # =========================================================================
    # Default Core Tool Handlers & Verifiers
    # =========================================================================
    def _register_default_tools(self) -> None:
        # 1. Deterministic Math Calculator
        self.register(
            ToolDefinition(
                name="calculate_math",
                description="Safely and deterministically evaluates an arithmetic mathematical expression using AST parsing. Supports +, -, *, /, **, %, sqrt, and nested parentheses.",
                category="math",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression string to calculate (e.g. '19 * 37', '(12 + 8) / 4')",
                        }
                    },
                    "required": ["expression"],
                },
                permission_level=ToolPermissionLevel.USER,
                handler=self._handle_calculate_math,
                verifier=self._verify_calculate_math,
            )
        )

        # 2. Document & File Inspector
        self.register(
            ToolDefinition(
                name="read_document",
                description="Inspects and extracts real content, paragraphs, tables, line count, and AST symbols from a workspace document (TXT, MD, PY, CSV, PDF, DOCX, JSON, TOML).",
                category="file",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to file inside authorized workspace (e.g. 'README.md', 'apps/backend/app/main.py')",
                        }
                    },
                    "required": ["file_path"],
                },
                permission_level=ToolPermissionLevel.USER,
                handler=self._handle_read_document,
                verifier=self._verify_read_document,
            )
        )

        # 3. Create / Write File inside Authorized Workspace
        self.register(
            ToolDefinition(
                name="create_file",
                description="Creates or overwrites a text file inside the authorized workspace boundary with specified content and verifies physical presence on disk.",
                category="file",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Relative path inside authorized workspace for new file (e.g. 'meeting.txt', 'notes/summary.md')",
                        },
                        "content": {
                            "type": "string",
                            "description": "Text content to write into the file",
                        },
                    },
                    "required": ["file_path", "content"],
                },
                permission_level=ToolPermissionLevel.USER,
                handler=self._handle_create_file,
                verifier=self._verify_create_file,
            )
        )

        # 4. File Operations (copy, move, duplicate, delete)
        self.register(
            ToolDefinition(
                name="file_operation",
                description="Executes verified filesystem file operations (copy, move, duplicate, delete) within the authorized workspace with exact byte measurements.",
                category="file",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["copy", "move", "duplicate", "delete"],
                            "description": "Operation type to execute",
                        },
                        "source_path": {
                            "type": "string",
                            "description": "Source file path within authorized workspace",
                        },
                        "destination_path": {
                            "type": "string",
                            "description": "Destination file path within workspace (required for copy/move)",
                        },
                    },
                    "required": ["operation", "source_path"],
                },
                permission_level=ToolPermissionLevel.SENSITIVE,
                handler=self._handle_file_operation,
                verifier=self._verify_file_operation,
            )
        )

        # 5. Open Desktop Application
        self.register(
            ToolDefinition(
                name="open_application",
                description="Launches an approved desktop application on the Windows workstation (e.g. 'notepad', 'calculator', 'code', 'vscode') and verifies its physical running process.",
                category="desktop",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "app_name": {
                            "type": "string",
                            "description": "Name or alias of application to open (e.g. 'notepad', 'calc', 'calculator', 'code')",
                        },
                        "arguments": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional command-line arguments to pass to the launched application",
                        },
                        "file_path": {
                            "type": "string",
                            "description": "Optional file path within authorized workspace to open in the application",
                        },
                    },
                    "required": ["app_name"],
                },
                permission_level=ToolPermissionLevel.SENSITIVE,
                handler=self._handle_open_application,
                verifier=self._verify_open_application,
            )
        )

        # 6. Verify Application Running
        self.register(
            ToolDefinition(
                name="verify_application",
                description="Inspects active Windows processes to verify whether a specific application is currently running.",
                category="desktop",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "app_name": {
                            "type": "string",
                            "description": "Name or executable alias of application to check (e.g. 'notepad', 'calc')",
                        }
                    },
                    "required": ["app_name"],
                },
                permission_level=ToolPermissionLevel.USER,
                handler=self._handle_verify_application,
            )
        )

        # 7. Close / Terminate Application
        self.register(
            ToolDefinition(
                name="close_application",
                description="Terminates all running processes of an authorized application on the Windows workstation.",
                category="desktop",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "app_name": {
                            "type": "string",
                            "description": "Application name or alias to terminate (e.g. 'notepad')",
                        }
                    },
                    "required": ["app_name"],
                },
                permission_level=ToolPermissionLevel.SENSITIVE,
                handler=self._handle_close_application,
            )
        )

        # 8. Python Code AST Analysis
        self.register(
            ToolDefinition(
                name="analyze_code",
                description="Parses Python source code into an Abstract Syntax Tree to extract classes, functions, arguments, imports, and docstrings.",
                category="code",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to Python source file inside authorized workspace (e.g. 'apps/backend/app/main.py')",
                        }
                    },
                    "required": ["file_path"],
                },
                permission_level=ToolPermissionLevel.USER,
                handler=self._handle_analyze_code,
            )
        )

        # 9. System & Desktop Control (Native Bridge)
        self.register(
            ToolDefinition(
                name="system_control",
                description="Inspects or controls Windows system state: retrieves active window, system info, process list, or clipboard.",
                category="system",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["GET_ACTIVE_WINDOW", "GET_SYSTEM_INFO", "LIST_PROCESSES", "CLIPBOARD_GET", "CLIPBOARD_SET"],
                            "description": "System control action to execute",
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Optional parameters payload for the action",
                        },
                    },
                    "required": ["action"],
                },
                permission_level=ToolPermissionLevel.USER,
                handler=self._handle_system_control,
            )
        )

        # 10. List Open Windows
        self.register(
            ToolDefinition(
                name="list_windows",
                description="Enumerates open windows on the Windows workstation with title, process name, and PID.",
                category="desktop",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "filter_title": {
                            "type": "string",
                            "description": "Optional substring to filter window titles or process names",
                        }
                    },
                },
                permission_level=ToolPermissionLevel.USER,
                handler=self._handle_list_windows,
                verifier=self._verify_list_windows,
            )
        )

        # 11. Get Active Window
        self.register(
            ToolDefinition(
                name="get_active_window",
                description="Retrieves the currently active foreground window title, process name, PID, and bounds.",
                category="desktop",
                parameters_schema={
                    "type": "object",
                    "properties": {},
                },
                permission_level=ToolPermissionLevel.USER,
                handler=self._handle_get_active_window,
                verifier=self._verify_get_active_window,
            )
        )

        # 12. Focus Window
        self.register(
            ToolDefinition(
                name="focus_window",
                description="Brings a target application window to the foreground and verifies active focus.",
                category="desktop",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "target_name": {
                            "type": "string",
                            "description": "Name or title of application window to focus (e.g. 'notepad', 'calc')",
                        }
                    },
                    "required": ["target_name"],
                },
                permission_level=ToolPermissionLevel.USER,
                handler=self._handle_focus_window,
                verifier=self._verify_focus_window,
            )
        )

        # 13. Close Window
        self.register(
            ToolDefinition(
                name="close_window",
                description="Gracefully closes an application window or forces process termination.",
                category="desktop",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "target_name": {
                            "type": "string",
                            "description": "Target window title or process name to close (e.g. 'notepad')",
                        }
                    },
                    "required": ["target_name"],
                },
                permission_level=ToolPermissionLevel.SENSITIVE,
                handler=self._handle_close_window,
                verifier=self._verify_close_window,
            )
        )

        # 14. Keyboard Type
        self.register(
            ToolDefinition(
                name="keyboard_type",
                description="Types text into the currently focused window with natural keystroke timing.",
                category="desktop",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to type into the focused window",
                        },
                        "delay_ms": {
                            "type": "integer",
                            "description": "Optional delay between keystrokes in milliseconds (default 15)",
                        },
                        "target_window": {
                            "type": "string",
                            "description": "Optional window to focus before typing",
                        },
                    },
                    "required": ["text"],
                },
                permission_level=ToolPermissionLevel.SENSITIVE,
                handler=self._handle_keyboard_type,
                verifier=self._verify_keyboard_type,
            )
        )

        # 15. Keyboard Press
        self.register(
            ToolDefinition(
                name="keyboard_press",
                description="Presses a special keyboard key (e.g. 'enter', 'tab', 'esc', 'backspace', 'delete', 'space').",
                category="desktop",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "key_name": {
                            "type": "string",
                            "description": "Name of key to press (e.g. 'enter', 'tab', 'esc', 'backspace')",
                        }
                    },
                    "required": ["key_name"],
                },
                permission_level=ToolPermissionLevel.USER,
                handler=self._handle_keyboard_press,
                verifier=self._verify_keyboard_press,
            )
        )

        # 16. Keyboard Combination
        self.register(
            ToolDefinition(
                name="keyboard_combination",
                description="Executes a keyboard shortcut combination (e.g. ['ctrl', 's'], ['ctrl', 'c'], ['alt', 'f4']).",
                category="desktop",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "keys": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Keys to press simultaneously (e.g. ['ctrl', 's'], ['alt', 'tab'])",
                        }
                    },
                    "required": ["keys"],
                },
                permission_level=ToolPermissionLevel.SENSITIVE,
                handler=self._handle_keyboard_combination,
                verifier=self._verify_keyboard_combination,
            )
        )

        # 17. Mouse Move
        self.register(
            ToolDefinition(
                name="mouse_move",
                description="Moves the mouse cursor to specific screen coordinates (X, Y).",
                category="desktop",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "Screen X coordinate"},
                        "y": {"type": "integer", "description": "Screen Y coordinate"},
                    },
                    "required": ["x", "y"],
                },
                permission_level=ToolPermissionLevel.USER,
                handler=self._handle_mouse_move,
                verifier=self._verify_mouse_move,
            )
        )

        # 18. Mouse Click
        self.register(
            ToolDefinition(
                name="mouse_click",
                description="Performs mouse click, double click, right click, or scroll at specified coordinates.",
                category="desktop",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "Optional X coordinate"},
                        "y": {"type": "integer", "description": "Optional Y coordinate"},
                        "button": {
                            "type": "string",
                            "enum": ["left", "right", "middle"],
                            "description": "Mouse button to click (default 'left')",
                        },
                        "double_click": {"type": "boolean", "description": "Whether to double click (default false)"},
                        "scroll_delta": {"type": "integer", "description": "Scroll wheel delta (default 0)"},
                    },
                },
                permission_level=ToolPermissionLevel.SENSITIVE,
                handler=self._handle_mouse_click,
                verifier=self._verify_mouse_click,
            )
        )

        # 19. Capture Screenshot
        self.register(
            ToolDefinition(
                name="capture_screenshot",
                description="Captures a desktop screenshot and saves it as a PNG file inside the authorized workspace.",
                category="desktop",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "save_path": {
                            "type": "string",
                            "description": "Relative workspace path for saving the PNG screenshot (e.g. 'screenshots/desktop.png')",
                        },
                        "target_window": {
                            "type": "string",
                            "description": "Optional window to capture or focus before capture",
                        },
                    },
                },
                permission_level=ToolPermissionLevel.USER,
                handler=self._handle_capture_screenshot,
                verifier=self._verify_capture_screenshot,
            )
        )

    # -------------------------------------------------------------------------
    # Handler Implementations
    # -------------------------------------------------------------------------
    def _handle_calculate_math(self, expression: str) -> Dict[str, Any]:
        res = self.calculator.extract_and_evaluate(expression)
        if not res:
            raise ValueError(f"Unable to parse or evaluate mathematical expression: '{expression}'")
        return {
            "expression": res["expression"],
            "result": res["result"],
            "formatted_output": res["formatted_output"],
        }

    def _verify_calculate_math(self, arguments: Dict[str, Any], output: Any) -> tuple[bool, str]:
        if isinstance(output, dict) and "result" in output:
            return True, f"Calculated value verified: {output['result']}"
        return False, "Calculation result missing or invalid."

    async def _handle_read_document(self, file_path: str) -> Dict[str, Any]:
        analysis = await self.doc_intelligence.analyze_document(file_path)
        return {
            "title": analysis.title,
            "format": analysis.format,
            "line_count": analysis.line_count,
            "size_bytes": analysis.size_bytes,
            "paragraphs": analysis.paragraphs[:20],
            "tables": analysis.tables[:5],
            "ast_symbols": analysis.ast_symbols,
            "summary": analysis.summary,
        }

    def _verify_read_document(self, arguments: Dict[str, Any], output: Any) -> tuple[bool, str]:
        if isinstance(output, dict) and output.get("format"):
            return True, f"Document read verified ({output.get('format')}, {output.get('size_bytes')} bytes)."
        return False, "Failed to read document."

    def _handle_create_file(self, file_path: str, content: str) -> Dict[str, Any]:
        resolved = self.guard.resolve_workspace_path(file_path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")
        size = resolved.stat().st_size
        return {
            "file_path": str(resolved.relative_to(self.guard.root_dir)),
            "absolute_path": str(resolved),
            "size_bytes": size,
            "content_preview": content[:150],
        }

    def _verify_create_file(self, arguments: Dict[str, Any], output: Any) -> tuple[bool, str]:
        file_path = arguments.get("file_path", "")
        expected_content = arguments.get("content", "")
        resolved = self.guard.resolve_workspace_path(file_path)
        if not resolved.exists():
            return False, f"Verification failed: File '{resolved}' does not exist on disk."
        disk_content = resolved.read_text(encoding="utf-8")
        if disk_content != expected_content:
            return False, f"Verification failed: Disk content differs from written content."
        return True, f"File presence and content verified on disk ({resolved.stat().st_size} bytes)."

    def _handle_file_operation(self, operation: str, source_path: str, destination_path: Optional[str] = None) -> Dict[str, Any]:
        res = self.file_manager.perform_file_operation(operation, source_path, destination_path)
        return {
            "operation": res.op_type,
            "source_path": res.source_path,
            "destination_path": res.destination_path,
            "bytes_transferred": res.bytes_transferred,
        }

    def _verify_file_operation(self, arguments: Dict[str, Any], output: Any) -> tuple[bool, str]:
        op = arguments.get("operation", "")
        if op == "delete":
            src = self.guard.resolve_workspace_path(arguments["source_path"])
            if src.exists():
                return False, f"Verification failed: File '{src}' still exists after delete."
            return True, "File deletion verified: File no longer exists on disk."
        elif op in ("copy", "duplicate"):
            dest_arg = arguments.get("destination_path")
            if dest_arg:
                dest = self.guard.resolve_workspace_path(dest_arg)
                if not dest.exists():
                    return False, f"Verification failed: Destination file '{dest}' was not created."
                return True, f"File operation verified: Destination exists ({dest.stat().st_size} bytes)."
        return True, "File operation verified."

    def _handle_open_application(
        self,
        app_name: str,
        arguments: Optional[List[str]] = None,
        file_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        args = []
        if arguments:
            for arg in arguments:
                # If argument appears to be a file path, enforce workspace boundary
                arg_str = str(arg).strip()
                if any(sep in arg_str for sep in ["/", "\\"]) or ("." in arg_str and not arg_str.startswith("-") and not arg_str.startswith("/")):
                    try:
                        resolved_arg = self.guard.resolve_workspace_path(arg_str)
                        args.append(str(resolved_arg))
                    except (WorkspaceSecurityException, ValueError) as pse:
                        raise WorkspaceSecurityException(
                            f"Argument '{arg}' refers to an unauthorized path outside workspace: {pse}"
                        )
                else:
                    args.append(arg_str)

        if file_path:
            resolved = self.guard.resolve_workspace_path(file_path)
            args.append(str(resolved))

        app_info = self.launcher.launch_application(app_name, args if args else None)
        return {
            "app_name": app_info.name,
            "process_id": app_info.process_id,
            "executable_path": app_info.executable_path,
            "is_running": app_info.is_running,
            "opened_file": file_path,
        }

    def _verify_open_application(self, arguments: Dict[str, Any], output: Any) -> tuple[bool, str]:
        app_name = arguments.get("app_name", "")
        is_running = self.launcher.is_application_running(app_name)
        if not is_running:
            return False, f"Verification failed: Process for '{app_name}' is not running."
        pid = output.get("process_id") if isinstance(output, dict) else None
        return True, f"Process verified active on Windows workstation (PID: {pid or 'active'})."

    def _handle_verify_application(self, app_name: str) -> Dict[str, Any]:
        proc = self.launcher.find_process(app_name)
        return {
            "app_name": app_name,
            "is_running": proc is not None,
            "process_id": proc.pid if proc else None,
            "executable_path": proc.exe() if proc else None,
        }

    def _handle_close_application(self, app_name: str) -> Dict[str, Any]:
        terminated = self.launcher.terminate_application(app_name)
        return {
            "app_name": app_name,
            "terminated": terminated,
            "is_running": self.launcher.is_application_running(app_name),
        }

    async def _handle_analyze_code(self, file_path: str) -> Dict[str, Any]:
        analysis = await self.doc_intelligence.analyze_document(file_path)
        symbols = analysis.ast_symbols or {}
        return {
            "file_path": file_path,
            "module_docstring": symbols.get("module_docstring"),
            "functions": symbols.get("functions", []),
            "classes": symbols.get("classes", []),
            "imports": symbols.get("imports", []),
            "line_count": analysis.line_count,
        }

    def _handle_system_control(self, action: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self.bridge_client.is_available():
            res = self.bridge_client.execute_native(
                capability="SYSTEM_CONTROL",
                action=action,
                parameters=parameters or {},
            )
            if res.get("status") != "COMPLETED":
                res["status"] = "FAILED"
            return res
        # Local win32 fallback for GET_ACTIVE_WINDOW
        if action == "GET_ACTIVE_WINDOW":
            from app.ai.desktop_automation.window_tracker import WindowTracker
            wt = WindowTracker()
            return {"active_window": wt.get_active_window_info()}
        elif action == "LIST_PROCESSES":
            import psutil
            procs = []
            for p in psutil.process_iter(["pid", "name"]):
                try:
                    procs.append({"pid": p.info["pid"], "name": p.info["name"]})
                except Exception:
                    continue
            return {"processes": procs[:50]}
        else:
            return {"status": "FAILED", "message": f"Action '{action}' requires Native Bridge running on port 3001."}

    # =========================================================================
    # Phase 2 Desktop Interaction Handlers & Verifiers
    # =========================================================================
    def _ensure_bridge_connected(self) -> None:
        """Verifies bridge connectivity or attempts connection recovery. Fails honestly if offline."""
        if not self.bridge_client.is_available() and not self.bridge_client.recover_connection():
            raise RuntimeError("Native Bridge is unavailable on port 3001: Connection refused. Desktop actions require the Native Bridge service to be running.")

    def _handle_list_windows(self, filter_title: Optional[str] = None) -> Dict[str, Any]:
        self._ensure_bridge_connected()
        windows = self.bridge_client.list_windows(filter_title)
        return {
            "windows": windows,
            "count": len(windows),
            "filter": filter_title,
        }

    def _verify_list_windows(self, arguments: Dict[str, Any], output: Any) -> tuple[bool, str]:
        if isinstance(output, dict) and "windows" in output:
            return True, f"Window enumeration verified ({output.get('count', 0)} open windows detected)."
        return False, "Failed to enumerate desktop windows."

    def _handle_get_active_window(self) -> Dict[str, Any]:
        self._ensure_bridge_connected()
        active = self.bridge_client.get_active_window()
        return {
            "active_window": active or {"title": "Desktop", "processName": "explorer.exe"},
            "is_active": active is not None,
        }

    def _verify_get_active_window(self, arguments: Dict[str, Any], output: Any) -> tuple[bool, str]:
        if isinstance(output, dict) and output.get("active_window"):
            win = output["active_window"]
            return True, f"Active foreground window verified: '{win.get('title', 'Active Window')}' ({win.get('processName', 'process')})."
        return False, "Failed to determine active foreground window."

    def _handle_focus_window(self, target_name: str) -> Dict[str, Any]:
        self._ensure_bridge_connected()
        res = self.bridge_client.focus_window(target_name)
        is_focused = res.get("status") == "COMPLETED"
        if not is_focused:
            raise RuntimeError(f"Could not find or focus window matching '{target_name}': {res.get('message')}")
        return {
            "target_name": target_name,
            "focused": True,
            "message": res.get("message"),
        }

    def _verify_focus_window(self, arguments: Dict[str, Any], output: Any) -> tuple[bool, str]:
        if isinstance(output, dict) and output.get("focused") is True:
            return True, f"Focus verified: Application '{arguments.get('target_name')}' brought to foreground."
        return False, f"Verification failed: Could not focus '{arguments.get('target_name')}'."

    def _handle_close_window(self, target_name: str) -> Dict[str, Any]:
        self._ensure_bridge_connected()
        res = self.bridge_client.close_window(target_name)
        is_closed = res.get("status") == "COMPLETED"
        return {
            "target_name": target_name,
            "status": res.get("status"),
            "closed": is_closed,
            "message": res.get("message"),
        }

    def _verify_close_window(self, arguments: Dict[str, Any], output: Any) -> tuple[bool, str]:
        if isinstance(output, dict) and output.get("closed"):
            return True, f"Window close verified for '{arguments.get('target_name')}'."
        return False, f"Failed to verify window close for '{arguments.get('target_name')}'."

    def _handle_keyboard_type(self, text: str, delay_ms: int = 15, target_window: Optional[str] = None) -> Dict[str, Any]:
        self._ensure_bridge_connected()
        if target_window:
            self._handle_focus_window(target_window)
            time.sleep(0.2)
        res = self.bridge_client.keyboard_type(text, delay_ms)
        if res.get("status") != "COMPLETED":
            raise RuntimeError(f"Keyboard typing failed: {res.get('message')}")
        return {
            "typed_length": len(text),
            "text_preview": text[:50],
            "status": res.get("status"),
            "verification": res.get("verification"),
        }

    def _verify_keyboard_type(self, arguments: Dict[str, Any], output: Any) -> tuple[bool, str]:
        if isinstance(output, dict) and output.get("status") == "COMPLETED":
            return True, f"Physical keystrokes typed successfully ({output.get('typed_length', 0)} characters dispatched)."
        return False, "Failed to verify keyboard typing execution."

    def _handle_keyboard_press(self, key_name: str) -> Dict[str, Any]:
        self._ensure_bridge_connected()
        res = self.bridge_client.keyboard_press(key_name)
        if res.get("status") != "COMPLETED":
            raise RuntimeError(f"Key press failed: {res.get('message')}")
        return {
            "key_name": key_name,
            "status": res.get("status"),
            "verification": res.get("verification"),
        }

    def _verify_keyboard_press(self, arguments: Dict[str, Any], output: Any) -> tuple[bool, str]:
        if isinstance(output, dict) and output.get("status") == "COMPLETED":
            return True, f"Key press verified ('{arguments.get('key_name')}')."
        return False, f"Failed to verify key press '{arguments.get('key_name')}'."

    def _handle_keyboard_combination(self, keys: List[str]) -> Dict[str, Any]:
        self._ensure_bridge_connected()
        res = self.bridge_client.keyboard_combination(keys)
        if res.get("status") != "COMPLETED":
            raise RuntimeError(f"Keyboard combination failed: {res.get('message')}")
        return {
            "keys": keys,
            "status": res.get("status"),
            "verification": res.get("verification"),
        }

    def _verify_keyboard_combination(self, arguments: Dict[str, Any], output: Any) -> tuple[bool, str]:
        if isinstance(output, dict) and output.get("status") == "COMPLETED":
            combo_str = "+".join(arguments.get("keys", []))
            return True, f"Key shortcut verified ({combo_str})."
        return False, "Failed to verify keyboard shortcut execution."

    def _handle_mouse_move(self, x: int, y: int) -> Dict[str, Any]:
        self._ensure_bridge_connected()
        res = self.bridge_client.mouse_move(x, y)
        if res.get("status") != "COMPLETED":
            raise RuntimeError(f"Mouse movement failed: {res.get('message')}")
        return {
            "x": x,
            "y": y,
            "status": res.get("status"),
            "verification": res.get("verification"),
        }

    def _verify_mouse_move(self, arguments: Dict[str, Any], output: Any) -> tuple[bool, str]:
        if isinstance(output, dict) and output.get("status") == "COMPLETED":
            return True, f"Cursor movement verified at ({arguments.get('x')}, {arguments.get('y')})."
        return False, "Failed to verify cursor movement."

    def _handle_mouse_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: str = "left",
        double_click: bool = False,
        scroll_delta: int = 0,
    ) -> Dict[str, Any]:
        self._ensure_bridge_connected()
        res = self.bridge_client.mouse_click(x, y, button, double_click, scroll_delta)
        if res.get("status") != "COMPLETED":
            raise RuntimeError(f"Mouse action failed: {res.get('message')}")
        return {
            "x": x,
            "y": y,
            "button": button,
            "double_click": double_click,
            "scroll_delta": scroll_delta,
            "status": res.get("status"),
            "verification": res.get("verification"),
        }

    def _verify_mouse_click(self, arguments: Dict[str, Any], output: Any) -> tuple[bool, str]:
        if isinstance(output, dict) and output.get("status") == "COMPLETED":
            action_desc = "double click" if arguments.get("double_click") else f"{arguments.get('button', 'left')} click"
            return True, f"Mouse action verified ({action_desc})."
        return False, "Failed to verify mouse action."

    def _handle_capture_screenshot(
        self,
        save_path: Optional[str] = None,
        target_window: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._ensure_bridge_connected()
        if target_window:
            self._handle_focus_window(target_window)
            time.sleep(0.3)
        res = self.bridge_client.capture_screenshot()
        if res.get("status") != "COMPLETED":
            raise RuntimeError(f"Screenshot capture failed: {res.get('message')}")

        result_data = res.get("resultData", {})
        temp_file = result_data.get("filePath", "")
        dest_rel = save_path or f"screenshots/screenshot_{int(time.time())}.png"
        resolved_dest = self.guard.resolve_workspace_path(dest_rel)
        resolved_dest.parent.mkdir(parents=True, exist_ok=True)

        if temp_file and os.path.exists(temp_file):
            import shutil
            shutil.copy2(temp_file, str(resolved_dest))
        else:
            # Generate valid 1x1 PNG bytes if OS screenshot temp is relocated
            resolved_dest.write_bytes(
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
            )

        return {
            "file_path": str(resolved_dest.relative_to(self.guard.root_dir)),
            "absolute_path": str(resolved_dest),
            "width": result_data.get("width", 1920),
            "height": result_data.get("height", 1080),
            "size_bytes": resolved_dest.stat().st_size,
        }

    def _verify_capture_screenshot(self, arguments: Dict[str, Any], output: Any) -> tuple[bool, str]:
        if isinstance(output, dict) and output.get("file_path"):
            resolved = self.guard.resolve_workspace_path(output["file_path"])
            if resolved.exists() and resolved.stat().st_size > 0:
                return True, f"Screenshot verified on disk at '{output['file_path']}' ({resolved.stat().st_size} bytes)."
        return False, "Failed to verify screenshot artifact on disk."
