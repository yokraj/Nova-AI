# Real Execution Rules

These rules govern real vs. simulated execution standards across Nova-AI.

## 1. No Replacement of Real Capabilities with Mocks
- Never replace working real execution logic with fake responses, stubbed methods, or mock implementations in production source code.
- Mocks belong strictly in isolated test files (`tests/unit/`) and must never be loaded in production execution paths.

## 2. Windows Physical Execution Verification
- Never report or claim a Windows desktop/system action succeeded unless physical execution was confirmed (e.g. checking process lists, window handles, file existence, screen state, or return codes).
- Simulated success returns (e.g., `return {"status": "success", "simulated": True}`) masquerading as real execution are strictly forbidden.

## 3. Capability Classification Standard
- Every subsystem capability must be explicitly classified and documented as one of:
  - **REAL**: Fully functional physical execution integrated end-to-end.
  - **PARTIAL**: Executable with specific boundary limitations or environmental pre-requisites.
  - **MOCK**: Simulated or stubbed response for isolated unit testing only.
  - **DISCONNECTED**: Backend capability built but missing frontend wiring or API exposure.
  - **BROKEN**: Runtime error or failing execution path requiring fix.

## 4. Security & Runtime Routing
- All native Windows computer control actions must route through the approved security and runtime pipeline:
  1. Permission Gate validation (`permission_manager.py`)
  2. Executable allowlisting check (`executable_validator.py` / `security_guard.py`)
  3. Security pipeline audit logging
  4. Real OS execution adapter (`automation/services.py` / `desktop_automation.py`)
