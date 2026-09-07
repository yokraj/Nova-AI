# Nova Architecture Rules

These rules govern architectural decisions across the Nova-AI codebase.

## 1. Deep Inspection Before Modification
- Before adding or modifying any feature, inspect existing documentation, architecture reports (`NOVA_COMPLETE_CODEBASE_AUDIT.md`, `NOVA_ARCHITECTURE_RECOMMENDATION.md`, etc.), and existing component implementations.
- Trace service calls across the stack before writing new logic.

## 2. Mandatory Service Reuse
- Check existing services in `apps/backend/app/services`, `apps/backend/app/core`, `apps/backend/app/automation`, `apps/backend/app/ai`, and `apps/backend/app/memory` before building new utility functions or services.
- Never write duplicate implementations for functionality that already exists (e.g. state management, session management, vector memory, execution engines).

## 3. Single Runtime Enforcement
- Never create a parallel runtime or duplicate engine for an existing capability.
- If a capability needs enhancement, extend the canonical engine or runtime cleanly with backwards compatibility.

## 4. Strict Subsystem Boundaries
- **Frontend (`apps/frontend/src`)**: Presentational UI, React components, state stores, and client-side HTTP/WebSocket communicators only. Business logic and system execution must remain on the backend.
- **Backend (`apps/backend/app`)**: Orchestration, API endpoints, LLM gateway, security pipelines, memory, agents, and service managers.
- **Native Bridge / OS Automation (`apps/backend/app/automation`, `apps/backend/app/core/native_bridge.py`, Win32 API adapters)**: System interaction layer. Must operate under backend security controls and permission validation.
