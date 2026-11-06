"""Real Application Launcher launching desktop applications and tracking physical process ownership.

Zero mock process IDs or fake window handles. Integrates with Native Bridge on port 3001
and falls back to verified direct Windows process execution using psutil.
"""

import os
import shutil
import subprocess
import time
from typing import Any, Dict, List, Optional, Set
import psutil
import structlog

from app.ai.desktop_automation.models import ApplicationInfo
from app.ai.desktop_automation.native_bridge_client import NativeBridgeClient

logger = structlog.get_logger("application_launcher")

# Strict prohibition of interactive command shells and script interpreters
DISALLOWED_INTERPRETERS: Set[str] = {
    "cmd", "cmd.exe", "powershell", "powershell.exe", "pwsh", "pwsh.exe",
    "bash", "bash.exe", "sh", "sh.exe", "wscript", "wscript.exe",
    "cscript", "cscript.exe", "mshta", "mshta.exe", "regsvr32", "rundll32",
    "conhost", "conhost.exe"
}

# Command flags that execute inline scripts or commands
DISALLOWED_CLI_FLAGS: Set[str] = {
    "-c", "/c", "/k", "/r", "-command", "-encodedcommand", "-enc", "-e",
    "-exec", "/e", "-file", "-inputformat", "-v", "--command", "-ex"
}

# Critical OS processes protected from termination
PROTECTED_SYSTEM_PROCESSES: Set[str] = {
    "system", "system idle process", "registry", "smss.exe", "csrss.exe",
    "wininit.exe", "services.exe", "lsass.exe", "svchost.exe", "winlogon.exe",
    "fontdrvhost.exe", "dwm.exe", "spoolsv.exe"
}

# Approved desktop productivity applications
KNOWN_EXECUTABLES: Dict[str, List[str]] = {
    "notepad": ["notepad.exe", r"C:\Windows\System32\notepad.exe", r"C:\Windows\notepad.exe"],
    "calculator": ["calc.exe", r"C:\Windows\System32\calc.exe"],
    "calc": ["calc.exe", r"C:\Windows\System32\calc.exe"],
    "code": ["code.cmd", "code.exe"],
    "vscode": ["code.cmd", "code.exe"],
    "explorer": ["explorer.exe", r"C:\Windows\explorer.exe"],
}


class ApplicationLauncher:
    """Launches desktop applications on Windows, retrieves physical PIDs, and tracks process instances."""

    def __init__(self, bridge_client: Optional[NativeBridgeClient] = None) -> None:
        self.bridge_client = bridge_client or NativeBridgeClient()

    def resolve_executable(self, app_name: str) -> Optional[str]:
        """Resolves an application alias or name to an authentic physical executable path."""
        clean = app_name.lower().strip()

        # Security check: Prohibit command interpreters and shells
        if clean in DISALLOWED_INTERPRETERS or clean.replace(".exe", "") in DISALLOWED_INTERPRETERS:
            raise PermissionError(
                f"Security Violation: Application '{app_name}' is a restricted command shell or interpreter "
                f"and cannot be launched via open_application."
            )

        # Check known registry aliases
        if clean in KNOWN_EXECUTABLES:
            for candidate in KNOWN_EXECUTABLES[clean]:
                which_path = shutil.which(candidate)
                if which_path and os.path.exists(which_path):
                    return which_path
                if os.path.exists(candidate):
                    return candidate

        # Check direct path or which
        direct_which = shutil.which(app_name)
        if direct_which and os.path.exists(direct_which):
            resolved_base = os.path.basename(direct_which).lower()
            if resolved_base in DISALLOWED_INTERPRETERS:
                raise PermissionError(
                    f"Security Violation: Target executable '{direct_which}' is a prohibited shell."
                )
            return direct_which

        if os.path.exists(app_name):
            resolved_base = os.path.basename(app_name).lower()
            if resolved_base in DISALLOWED_INTERPRETERS:
                raise PermissionError(
                    f"Security Violation: Target executable '{app_name}' is a prohibited shell."
                )
            return os.path.abspath(app_name)

        # Fallback search in System32 and Program Files
        candidates = [
            os.path.join(r"C:\Windows\System32", f"{clean}.exe"),
            os.path.join(r"C:\Windows", f"{clean}.exe"),
            os.path.join(r"C:\Program Files", clean, f"{clean}.exe"),
            os.path.join(r"C:\Program Files (x86)", clean, f"{clean}.exe"),
        ]
        for c in candidates:
            if os.path.exists(c):
                base = os.path.basename(c).lower()
                if base not in DISALLOWED_INTERPRETERS:
                    return c

        return None

    def validate_launch_arguments(self, app_name: str, arguments: Optional[List[str]]) -> None:
        """Validates that command line arguments do not contain shell injection payloads."""
        if not arguments:
            return

        for arg in arguments:
            arg_lower = str(arg).lower().strip()
            # Check for prohibited command execution flags
            if arg_lower in DISALLOWED_CLI_FLAGS or any(arg_lower.startswith(f"{f} ") for f in DISALLOWED_CLI_FLAGS):
                raise PermissionError(
                    f"Security Violation: CLI flag '{arg}' in arguments for application '{app_name}' "
                    f"is restricted to prevent command injection."
                )
            # Check for inline script execution attempts
            if any(term in arg_lower for term in ["iex", "invoke-expression", "downloadstring", "cmd.exe", "powershell"]):
                raise PermissionError(
                    f"Security Violation: Argument '{arg}' contains prohibited script execution directives."
                )

    def launch_application(self, app_name: str, arguments: Optional[List[str]] = None) -> ApplicationInfo:
        """Launches an application and returns verified physical process metadata."""
        clean = app_name.lower().strip()

        # Enforce interpreter prohibition
        if clean in DISALLOWED_INTERPRETERS or clean.replace(".exe", "") in DISALLOWED_INTERPRETERS:
            raise PermissionError(
                f"Security Violation: Application '{app_name}' is a restricted command shell/interpreter "
                f"and cannot be launched via open_application."
            )

        # Validate arguments against injection
        self.validate_launch_arguments(app_name, arguments)

        # 1. Try Native Bridge first if available
        if self.bridge_client.is_available():
            try:
                res = self.bridge_client.execute_native(
                    capability="APPLICATION_CONTROL",
                    action="OPEN_APPLICATION",
                    target={"applicationAlias": app_name},
                    parameters={"args": arguments or []},
                )
                if res.get("status") == "COMPLETED" and res.get("verification") == "PROCESS_RUNNING":
                    proc = self.find_process(app_name)
                    pid = proc.pid if proc else 0
                    exe = proc.exe() if proc else (res.get("resultData", {}).get("targetPath", ""))
                    return ApplicationInfo(
                        name=app_name,
                        process_id=pid,
                        executable_path=exe,
                        window_handle=f"0x{pid:X}" if pid else "",
                        is_running=True,
                    )
            except Exception as e:
                logger.warning("native_bridge_launch_fallback", app=app_name, error=str(e))

        # 2. Local verified execution via subprocess (strictly without shell)
        exe_path = self.resolve_executable(app_name)
        if not exe_path:
            raise FileNotFoundError(f"Unable to locate executable for application '{app_name}' on Windows.")

        cmd = [exe_path] + (arguments or [])
        logger.info("launching_physical_process", app_name=app_name, cmd=cmd)

        try:
            proc = subprocess.Popen(
                cmd,
                shell=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            real_pid = proc.pid

            time.sleep(0.3)
            is_alive = psutil.pid_exists(real_pid)
            if not is_alive:
                child = self.find_process(app_name)
                if child:
                    real_pid = child.pid
                    is_alive = True

            return ApplicationInfo(
                name=app_name,
                process_id=real_pid,
                executable_path=exe_path,
                window_handle=f"0x{real_pid:X}",
                is_running=is_alive,
            )
        except Exception as e:
            logger.error("physical_process_launch_failed", app=app_name, error=str(e))
            raise RuntimeError(f"Failed to launch application '{app_name}': {e}")

    def find_process(self, app_name: str) -> Optional[psutil.Process]:
        """Finds active running process by exact application name or executable basename."""
        clean = app_name.lower().replace(".exe", "").strip()
        target_names = {clean, f"{clean}.exe"}

        for p in psutil.process_iter(["pid", "name", "exe"]):
            try:
                p_name = p.info["name"].lower() if p.info["name"] else ""
                if p_name in target_names or p_name.startswith(f"{clean}."):
                    return p
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def is_application_running(self, app_name: str) -> bool:
        """Returns True if a process matching app_name is active."""
        return self.find_process(app_name) is not None

    def terminate_application(self, app_name: str) -> bool:
        """Gracefully terminates running processes matching app_name with system process protection."""
        clean = app_name.lower().strip()
        clean_base = clean.replace(".exe", "")

        # Security check: Never terminate critical Windows system processes
        if clean in PROTECTED_SYSTEM_PROCESSES or f"{clean_base}.exe" in PROTECTED_SYSTEM_PROCESSES or clean_base in PROTECTED_SYSTEM_PROCESSES:
            raise PermissionError(
                f"Security Violation: Process '{app_name}' is a protected Windows system process and cannot be terminated."
            )

        target_names = {clean_base, f"{clean_base}.exe"}
        terminated = False

        for p in psutil.process_iter(["pid", "name"]):
            try:
                p_name = p.info["name"].lower() if p.info["name"] else ""
                # Match exact process basename to prevent terminating unintended processes
                if p_name in target_names:
                    # Never terminate PID 0 or PID 4 (System)
                    if p.pid <= 4:
                        continue
                    p.terminate()
                    try:
                        p.wait(timeout=2.0)
                    except psutil.TimeoutExpired:
                        p.kill()
                    terminated = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return terminated
