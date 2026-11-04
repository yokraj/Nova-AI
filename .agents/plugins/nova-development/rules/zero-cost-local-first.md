# Zero-Cost Local-First Rules — Permanent Nova Policy

These rules enforce Nova-AI's non-negotiable permanent zero-cost, local-first operational directive across all development phases.

## 1. Absolute Zero-Cost Guarantee
- Zero paid dependencies, zero commercial API subscriptions, zero usage-metered platforms.
- Prohibited: OpenAI, Anthropic, Gemini Paid API, ElevenLabs, paid cloud hosting, paid cloud databases, or services requiring credit card / billing registration.
- Any dependency or model introduced must be 100% free and open-source or built into the local operating system.

## 2. Local-First Model & Execution Preference
- Primary LLM reasoning: Local Ollama (Qwen2.5-Coder, Qwen3, Llama 3, DeepSeek-R1).
- Primary Speech Recognition (STT): Local faster-whisper in `.venv-stt` (100% offline).
- Primary Text-to-Speech (TTS): Local Windows System SAPI / Piper ONNX (100% offline).
- Optional Online Services (such as free Edge-TTS): Must remain strictly optional, non-blocking, and clearly labeled as online free services. Core functionality must never depend on them.
- Primary Database: Local SQLite or local PostgreSQL.

## 3. Secret & API Key Hygiene
- Never introduce or require commercial paid API keys.
- Never hardcode secrets or credentials into source code or committed artifacts.
- Enforce `offline_mode: True` as the primary configuration across voice and AI subsystems.

## 4. Zero Telemetry & Privacy Preservation
- Never introduce external telemetry, tracking, or remote analytics.
- User data, conversation logs, voice audio, and computer control context must remain strictly local to the user's machine.

## 5. Cost Transparency & Evaluation Before Adding Dependencies
- Before adding any package or service, evaluate:
  1. Completely free ($0.00)?
  2. Open-source or free license?
  3. No account / API key / billing required?
  4. Local execution supported?
  5. No usage-based paid tiers or paywalls?
- Always report cost transparency metadata to the user.

## 6. Process & Workflow Discipline
- Strictly NO Git commands (`git status`, `git add`, `git commit`, `git push`, etc.).
- Strictly DO NOT start, stop, restart, or kill server processes. Provide exact commands for the user.
- Strictly DO NOT run automated test runners (`pytest`, `vitest`, `pnpm test`). The user performs testing manually.

## 7. Phase 3 Enforced Protections
- **ZeroCostPolicy Guard**: `apps/backend/app/core/zero_cost_policy.py` blocks commercial AI APIs before invocation.
- **Failover Restricted**: `apps/backend/app/inference/fallback.py` cascade is restricted to local Ollama models.
- **TTS Offline Priority**: `apps/frontend/src/features/voice/types/voiceSettings.ts` defaults to `nova-offline` (Windows SAPI). Online Edge-TTS is strictly opt-in.
- **Realistic Voice Declarations**: Wake word is classified as local Whisper keyword matching; Piper is flagged as unconfigured until local model files are added.

## 8. Young Female Voice System Specifications
- **Offline Female Voice (Default)**: Windows SAPI `Microsoft Zira Desktop` tuned to pitch `1.08` and rate `1.05`. 100% offline local execution.
- **Neural Female Voice (Optional Online)**: Microsoft Edge TTS (`en-IN-NeerjaNeural`, `ta-IN-PallaviNeural`, `hi-IN-SwaraNeural`). Explicit opt-in only.
- **Dynamic Voice Discovery**: Dynamically queries installed Windows SAPI voices; never hardcodes unavailable voices.
- **Preview Transparency**: Live voice preview returns actual server engine status (`OFFLINE` vs `ONLINE`). Never disguises online calls as local.
