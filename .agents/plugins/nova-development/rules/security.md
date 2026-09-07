# Security Rules

These rules enforce strict security constraints across all Nova-AI subsystems.

## 1. Non-Bypassable Permission Gates
- Never bypass or disable permission evaluation gates (`PermissionManager`, action elevation prompts, user confirmation dialogs).
- Any action modifying system state, launching executables, writing files, or sending network traffic must evaluate user permissions.

## 2. Strict Executable Allowlisting
- Never weaken or bypass executable path validation or allowlist checks.
- Executables must be explicitly validated against approved directories and cryptographic/path constraints before launching.

## 3. Protected Process & System Safety
- Never remove or relax protected-process restrictions, system file protections, or OS privilege boundaries.
- Hazardous system operations (registry modification, system binary termination, raw device access) are blocked by default.

## 4. Prompt Injection Defenses
- Never bypass or remove prompt injection defense filters (`prompt_injection.py`, input sanitization layers).
- Untrusted user input, external web data, file contents, or voice transcripts must pass through injection detection before reaching the AI planning or tool selection engines.

## 5. Secret Protection
- Never expose secrets, credentials, tokens, or encryption keys in API responses, log files, stdout, error tracebacks, or UI states.

## 6. Prohibition of Unsanitized Shell Execution
- Never pass natural-language strings directly into shell interpreters (`cmd.exe`, `powershell.exe`, `sh`, `subprocess.Popen(shell=True)`) without strict argument parsing, allowlisting, and parameter validation.
