# Zero-Cost Local-First Rules

These rules enforce Nova-AI's zero-cost, local-first operational directive.

## 1. Local-First Model & Service Preference
- Prioritize local open-source models (Ollama, vLLM, local HuggingFace/GGUF models) and local databases/services (SQLite, local ChromaDB, local FAISS, Whisper local).
- Self-hosted or local execution is the primary runtime choice for all AI, vector, voice, and compute tasks.

## 2. Prohibition of Unapproved Cloud/Paid APIs
- Do not introduce external paid APIs (e.g. OpenAI, Anthropic, Google Cloud, AWS) or cloud dependencies without explicit, written user approval.
- Any network requests to external third-party services must be strictly opt-in and configurable via environment variables.

## 3. Secret & API Key Hygiene
- Never hardcode API keys, secrets, tokens, or credentials into source code, configuration files, or committed artifacts.
- Use `.env.example` templates and load secrets strictly from environment variables or secure local stores.

## 4. Zero Telemetry & Privacy Preservation
- Never introduce silent external telemetry, user tracking, data collection, or remote phone-home mechanisms.
- User data, conversation logs, voice audio, and computer control context must remain strictly local to the user's machine unless explicitly configured by the user.
