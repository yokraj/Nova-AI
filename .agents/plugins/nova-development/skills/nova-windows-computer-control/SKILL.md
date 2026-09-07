---
name: nova-windows-computer-control
description: >-
  Detailed manual for Windows desktop automation, application discovery, window manipulation, input injection, screenshot capture, clipboard management, and security restrictions in Nova-AI.
---

# Nova Windows Computer Control Skill

Use this skill when developing, debugging, auditing, or testing Windows desktop automation, process management, vision control, or native OS interaction capabilities.

## Subsystem Architecture Overview

The computer control subsystem is located in `apps/backend/app/automation/` and `apps/backend/app/core/native_bridge.py`:
- `automation/services.py`: Primary desktop automation adapter (PyAutoGUI, Win32, UI Automation).
- `automation/desktop_automation.py`: High-level action coordinator.
- `security/permission_manager.py`: Permission gate and elevation checker.
- `security/executable_validator.py`: Executable path allowlist enforcement.

## Computer Control Capabilities & Verification Protocols

### 1. Application Discovery & Launching
- **Discovery**: Enumerates installed applications via Start Menu shortcuts, Registry, and PATH entries.
- **Validation**: Every executable path MUST pass `ExecutableValidator` allowlist checking before `subprocess.Popen` or Win32 `ShellExecute` is invoked.
- **Verification**: Check target process PID via `psutil.process_iter()`.

### 2. Window Management
- **Operations**: Focus, minimize, maximize, restore, move, resize, close window.
- **Verification**: Query window bounding rects using `pygetwindow` or Win32 `GetWindowRect`.

### 3. Mouse & Keyboard Injection
- **Input Types**: Click, double-click, right-click, drag, scroll, type text, hotkey combinations.
- **Safety Safeguards**: `pyautogui.FAILSAFE = True` must remain active to allow top-left corner emergency abort.
- **Verification**: Confirm input focus state and target window reaction.

### 4. Clipboard & Screenshot Management
- **Clipboard**: Read/write system clipboard text and image formats securely.
- **Screenshots**: Capture full desktop or targeted window region, convert to PNG/JPEG bytes for vision analysis.

### 5. Security Restrictions
- Block attempts to automate restricted system dialogs (UAC prompts, Task Manager, security settings) unless running under elevated administrator context with user confirmation.
- Log every automated action to the security audit trail.
