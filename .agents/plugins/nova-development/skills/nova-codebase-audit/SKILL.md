---
name: nova-codebase-audit
description: >-
  Perform full repository architecture inspection, classify capabilities into REAL, PARTIAL, MOCK, DISCONNECTED, or BROKEN, and verify frontend/backend integration points.
---

# Nova Codebase Audit Skill

Use this skill when auditing Nova-AI codebase health, verifying component connectivity, assessing system readiness, or categorizing capability implementations.

## Workflow Instructions

### 1. Repository-Wide Architecture Inspection
1. Inspect the workspace root reports (`NOVA_COMPLETE_CODEBASE_AUDIT.md`, `NOVA_FEATURE_MATRIX.md`, `NOVA_AUDIT_SUMMARY.md`, `NOVA_FRONTEND_BACKEND_INTEGRATION_AUDIT.md`).
2. Verify system module locations:
   - Backend APIs & Services: `apps/backend/app/`
   - Native Automation & Win32 Control: `apps/backend/app/automation/`, `apps/backend/app/core/native_bridge.py`
   - AI Gateway & LLM Orchestration: `apps/backend/app/ai/`, `apps/backend/app/inference/`
   - Voice Subsystem: `apps/backend/app/voice/`
   - Memory & RAG: `apps/backend/app/memory/`, `apps/backend/app/vector_memory/`, `apps/backend/app/rag/`
   - Security & Permission Gate: `apps/backend/app/security/`
   - Frontend React SPA: `apps/frontend/src/`

### 2. Capability Classification Matrix
For each inspected feature or module, assign one of the following statuses:
- **REAL**: Production code connected end-to-end to real OS/hardware/model APIs with physical execution.
- **PARTIAL**: Implemented real backend functionality, but missing full options, edge case handling, or UI controls.
- **MOCK**: Synthetic or stubbed response suitable for isolated unit testing only.
- **DISCONNECTED**: Backend service exists and passes unit tests, but is not exposed via API endpoints or frontend UI components.
- **BROKEN**: Runtime error, invalid import, syntax error, or failing execution path.

### 3. Frontend / Backend Integration Verification
1. Compare API endpoint definitions in `apps/backend/app/api/` and `apps/backend/app/main.py` against frontend API service calls in `apps/frontend/src/services/` and `apps/frontend/src/api/`.
2. Inspect WebSocket channel subscriptions in `apps/backend/app/websocket/` against Zustand state stores or custom hooks in `apps/frontend/src/store/` and `apps/frontend/src/hooks/`.
3. Check payload schemas for parameter mismatches, missing fields, or unhandled response states.

### 4. Audit Deliverables
When running an audit, generate or update a structured audit summary covering:
- Total components audited
- Capability breakdown counts (REAL, PARTIAL, MOCK, DISCONNECTED, BROKEN)
- Critical disconnects and recommended remediation steps
