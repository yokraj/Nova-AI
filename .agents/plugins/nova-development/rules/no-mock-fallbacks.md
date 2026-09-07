# No Mock Fallbacks Rules

These rules forbid silent fallbacks from real execution to mock data in production runtime pathways.

## 1. No Silent Fallback to Fake Outputs
- If a real hardware, OS capability, voice runtime, or local LLM engine fails or is unavailable, the system must return a clear, explicit error message describing the failure.
- Never catch an operational failure silently and fall back to dummy/simulated data while claiming the action succeeded.

## 2. Truthful Availability Reporting
- If a required local model, audio driver, PyAutoGUI dependency, Win32 handle, or service daemon is missing, report `RuntimeUnavailable` or equivalent explicit exception.
- Display the exact missing dependency and remediation steps to the user.

## 3. Strict Boundary for Mocks
- Existing mock objects, fixture generators, and synthetic data helpers are allowed ONLY in `tests/` directories for offline unit testing.
- Production modules in `apps/backend/app/` must NEVER import or fall back to mock objects at runtime.
