# Nova Master Current Architecture Report

## Executive Summary

This document presents the authoritative architectural blueprint of **Nova-AI** derived directly from the verified codebase inspection following Phase F1.51.

---

## 1. Single Canonical Production Pipeline

Nova-AI operates through one unified, single-direction production execution pipeline:

$$\text{USER VOICE / TEXT} \longrightarrow \text{UNIVERSAL COMMAND HOOK} \longrightarrow \text{AGENT RUNTIME} \longrightarrow \text{LOCAL LLM (OLLAMA)} \longrightarrow \text{PLAN VALIDATOR} \longrightarrow \text{PERMISSION GUARD} \longrightarrow \text{TOOL EXECUTOR} \longrightarrow \text{NATIVE BRIDGE CLIENT} \longrightarrow \text{WINDOWS OS} \longrightarrow \text{VISUAL VERIFICATION} \longrightarrow \text{RECOVERY ENGINE} \longrightarrow \text{COMPLETED RESPONSE}$$

---

## 2. Layer-by-Layer Architectural Breakdown

### Layer 1: Universal Command Surface & UI
- **File**: [useUniversalCommand.ts](file:///c:/Projects/Nova-AI/apps/frontend/src/features/universal-command/hooks/useUniversalCommand.ts)
- Accepts text input or Web Speech API voice input (`source='VOICE'`).
- Dispatches raw user goal directly to `AgentRuntime.executeGoal()`.

### Layer 2: Autonomous AI Runtime & Local Model Reasoning
- **Files**: [agentRuntime.ts](file:///c:/Projects/Nova-AI/apps/frontend/src/features/ai-runtime/runtime/agentRuntime.ts) & [localModelProvider.ts](file:///c:/Projects/Nova-AI/apps/frontend/src/features/ai-runtime/providers/localModelProvider.ts)
- Connects to local Ollama / OpenAI gateway on `127.0.0.1:11434/v1` for zero-cost offline NLU and structured JSON execution plan generation.
- Checks active OS tasklist and foreground window metadata to reason dynamically (e.g. focus running processes instead of launching duplicates).

### Layer 3: Security Policy & Permission Evaluation
- **Files**: [toolPermissionGuard.ts](file:///c:/Projects/Nova-AI/apps/frontend/src/features/ai-runtime/security/toolPermissionGuard.ts), [bridgeSecurityGuard.ts](file:///c:/Projects/Nova-AI/apps/frontend/src/features/native-bridge/security/bridgeSecurityGuard.ts), and [agentPolicy.ts](file:///c:/Projects/Nova-AI/apps/frontend/src/features/ai-runtime/security/agentPolicy.ts)
- Validates plan schema via `PlanValidator`.
- Flags high-risk or elevated operations as `requiresApproval = true` and `requiresElevation = true`.
- Sanitizes prompt injection tokens and checks raw target strings for command injection characters (`&&`, `;`, `|`, `` ` ``).

### Layer 4: Tool Routing & Native Execution
- **Files**: [toolExecutor.ts](file:///c:/Projects/Nova-AI/apps/frontend/src/features/ai-runtime/tool-router/toolExecutor.ts) & [nativeBridgeClient.ts](file:///c:/Projects/Nova-AI/apps/frontend/src/features/native-bridge/client/nativeBridgeClient.ts)
- Maps structured tool calls (`application.open`, `filesystem.read_file`, `windows_type_text`, `windows_mouse_click`) to `NativeBridgeClient.executeNative()`.
- Communicates with Native Bridge HTTP service on `http://127.0.0.1:3001/api/v1/native-execute`.

### Layer 5: Native Bridge Server & Win32 Interop
- **Files**: [nativeBridgeServer.ts](file:///c:/Projects/Nova-AI/apps/frontend/src/features/native-bridge/server/nativeBridgeServer.ts) & [windowsNativeHelper.ts](file:///c:/Projects/Nova-AI/apps/frontend/src/features/native-bridge/server/windowsNativeHelper.ts)
- Executes real Win32 C/C++ / C# PowerShell interop for multi-monitor screenshot capture (`VirtualScreen`), active window queries, physical mouse/keyboard/clipboard control, application discovery (363+ apps), and legitimate `Start-Process -Verb RunAs` elevation.

### Layer 6: Visual Grounding & Post-Action Verification
- **Files**: [visionOrchestrator.ts](file:///c:/Projects/Nova-AI/apps/frontend/src/features/vision/orchestrator/visionOrchestrator.ts) & [visualTargetResolver.ts](file:///c:/Projects/Nova-AI/apps/frontend/src/features/vision/resolvers/visualTargetResolver.ts)
- Implements 9-stage visual execution loop (`SEE` $\rightarrow$ `UNDERSTAND` $\rightarrow$ `GROUND` $\rightarrow$ `SECURITY` $\rightarrow$ `ACT` $\rightarrow$ `OBSERVE` $\rightarrow$ `VERIFY` $\rightarrow$ `RECOVER` $\rightarrow$ `COMPLETE`).
- Re-captures desktop display post-action to empirically verify target state changes.

---

## 3. Disconnected & Mock System Isolation Status

- **Production Execution Mock Fallbacks**: **0**.
- **Silent Cloud Fallbacks**: **0**.
- **Mock / Test Only Code**: Strictly isolated in `mock/` subdirectories for offline unit tests.
