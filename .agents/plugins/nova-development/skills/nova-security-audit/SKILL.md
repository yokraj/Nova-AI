---
name: nova-security-audit
description: >-
  Security auditing runbook for verifying permission gates, prompt injection defenses, path sanitization, executable allowlists, process protection, and secret leakage prevention.
---

# Nova Security Audit Skill

Use this skill when auditing Nova-AI for vulnerability exposure, inspecting permission models, testing prompt injection defenses, validating path security, or scanning for exposed secrets.

## Audit Checklist & Procedures

### 1. Permission Gate Audit (`permission_manager.py`)
- Verify that every action with side-effects (file write, app launch, process kill, network call) calls `permission_manager.check_permission()`.
- Ensure permission rules cannot be bypassed by client-supplied payload parameters (e.g. `skip_permission_check=True`).

### 2. Prompt Injection Defense Audit (`prompt_injection.py`)
- Test injection detector against standard attack vectors:
  - System prompt override attempts ("Ignore previous instructions...")
  - Indirect prompt injections in web scrape content, file reads, or voice input.
  - Delimiter escape sequences.
- Verify injection attempts raise `PromptInjectionDetectedException` and block execution.

### 3. Path Traversal & Executable Validation (`executable_validator.py`)
- Inspect file system APIs for directory traversal vulnerabilities (`../`, `..\`, absolute system paths outside workspace).
- Verify executable launcher checks targets against approved executable allowlists (`C:\Program Files\`, `C:\Windows\System32\`, explicitly allowed paths).

### 4. Secret & Credential Scanning
- Search codebase and configuration templates for hardcoded API keys, JWT secrets, passwords, or tokens:
  - Regex patterns: `(?i)(api_key|secret|password|bearer|private_key)\s*[:=]\s*['"][A-Za-z0-9_\-]{8,}['"]`
- Verify `.env` is listed in `.gitignore` and `.env.example` contains only placeholder values.

### 5. Automated Security Reports
- Run security test script / report generator:
  ```powershell
  pytest tests/security/
  ```
- Inspect `NOVA_SECURITY_AUDIT.md` and update finding metrics.
