# NOVA AI — PERMANENT ZERO-COST DEVELOPMENT POLICY

## 1. Non-Negotiable Project Principle
Nova AI is strictly developed using a **100% zero-cost technology stack**.

The project must not depend on paid APIs, paid tools, paid subscriptions, commercial AI services, or paid third-party platforms. This is a permanent, non-negotiable architectural requirement for the entire Nova AI project across all phases, features, integrations, upgrades, and deployments.

---

## 2. Strictly Prohibited
Under no circumstances shall any of the following be introduced or integrated:
- **Paid AI / LLM APIs**: OpenAI API, Anthropic Claude API, Google Gemini Paid API, Groq paid tiers, or equivalent commercial endpoints.
- **Paid Speech Services**: Paid Speech-To-Text (STT) or Text-To-Speech (TTS) services (e.g. ElevenLabs, Google Cloud Text-to-Speech paid tiers, Amazon Polly paid tiers).
- **Paid Cloud Hosting / Compute**: Mandatory AWS, Azure, Google Cloud compute, paid VPS, or serverless compute.
- **Paid Cloud Databases**: Supabase paid tiers, Pinecone, Neon, CockroachDB paid tiers, or managed cloud vector stores.
- **Paid Automation & Vision**: Paid Zapier/Make platforms, commercial OCR APIs, paid image generation endpoints.
- **Paid Developer Tools**: Paid SDKs, proprietary closed libraries, commercial telemetry, or usage-metered packages.
- **Trial / Credit Traps**: Any platform or service that offers "free trial" credits followed by mandatory billing or credit card registration.

---

## 3. Preferred Technology Strategy
All Nova AI capabilities are built using local-first, free, and open-source foundations:

| Domain | Technology / Stack | License & Cost | Execution Mode |
| :--- | :--- | :--- | :--- |
| **Core LLM & Reasoning** | Ollama with Qwen2.5-Coder / Qwen3, Llama 3, DeepSeek-R1 | Open Source / Free Weights | 100% Local (CPU/GPU) |
| **Speech Recognition (STT)** | faster-whisper (CTranslate2 & ONNX) | MIT / Apache 2.0 (Zero Cost) | 100% Local Offline |
| **Text-to-Speech (TTS)** | Windows SAPI / System Speech Synthesizer / Piper ONNX | Open Source / Built-in OS | 100% Local Offline |
| **Optional Free TTS** | Edge-TTS (optional high-definition voice option) | LGPLv3 (Zero Cost, No Account) | Online (Optional Only) |
| **Desktop Automation** | Windows Win32 API / UI Automation via Native Bridge | MIT / Built-in Windows | 100% Local Desktop |
| **Computer Vision / OCR** | OpenCV, PaddleOCR, EasyOCR, YOLO local weights | Apache 2.0 / Free | 100% Local Offline |
| **Database & Vector Storage** | SQLite / aiosqlite, Local PostgreSQL, Local ChromaDB / FAISS | Open Source (Zero Cost) | 100% Local Machine |
| **Backend & Frontend** | FastAPI, Python 3.11/3.14, React 19, TypeScript, Vite, Tailwind | MIT (Zero Cost) | 100% Local Machine |

---

## 4. Internet and Cloud Restrictions
- **Local-First Core**: Nova's core features (command execution, reasoning, desktop interaction, voice recognition, database, memory) must function entirely offline.
- **Optional Online Features**: Any network-dependent service must be strictly optional and clearly distinguished from offline capabilities.
- **Zero Mandatory External Servers**: Nova must never fail to start or operate simply because an internet connection is unavailable.
- **Zero Silent Telemetry**: Private user data, screen context, keystrokes, and audio recordings must never leave the user's physical machine without explicit permission.

---

## 5. Mandatory Evaluation Checklist Before Adding Any Dependency
Every new library, model, SDK, or service must satisfy all seven criteria before adoption:
1. **Completely Free?** Yes, 100% free with no payment required.
2. **Open-Source / Free License?** Legally usable without commercial licenses or purchase.
3. **No Account / No Credit Card / No API Key?** Requires zero subscriptions or billing accounts.
4. **Local Execution?** Operates locally on the host machine or has a local-first offline path.
5. **No Hidden Costs?** Zero usage-based throttling requiring payment to unlock.
6. **No Redistribution / Commercial Barriers?** Fully compliant with open project distribution.
7. **Best Free Alternative Selected?** Chosen because it represents the highest quality zero-cost option available.

---

## 6. Protocol for Features Requiring Paid Services
If a requested capability typically uses a commercial service:
1. Search exclusively for free, local, or open-source alternatives.
2. Prioritize local algorithms and models runnable on existing hardware.
3. If no viable zero-cost solution exists, clearly explain the technical trade-offs to the user.
4. Never introduce a paid solution silently, register billing, or add commercial SDKs.

---

## 7. Cost Transparency Reporting
Every newly introduced dependency or service must report:
- **Name**: Component or library name.
- **Purpose**: Specific capability enabled.
- **License**: Exact open-source or permissive license.
- **Cost**: Explicitly verified as $0.00 / Zero Cost.
- **Execution Mode**: Local Offline vs. Optional Online.
- **Authentication**: Confirm no account or paid API key is needed.
- **Usage Limits**: Confirm no paywalls or metered billing apply.

---

## 8. Development & Workflow Constraints
- **Zero Git Operations**: Never execute `git` commands (`status`, `add`, `commit`, `push`, etc.).
- **Zero Process Manipulation**: Never start, stop, restart, or kill server processes. Provide exact terminal commands for the user to execute manually.
- **Zero Automated Test Runners**: Do not trigger automated test runners (`pytest`, `vitest`, `pnpm test`) without explicit user instruction. Manual testing is performed by the user.
- **Zero Mock Fallbacks Masquerading as Real Execution**: All actions must be genuinely executed.

---

## 9. Phase 3 Hardened Enforcement Architecture
As of Phase 3, the Zero-Cost Policy is hard-coded and enforced directly inside the runtime execution paths:
1. **Central Policy Engine**: [`ZeroCostPolicy`](file:///c:/Projects/Nova-AI/apps/backend/app/core/zero_cost_policy.py) intercepts and validates all provider requests, rejecting commercial providers with `ZeroCostPolicyViolation`.
2. **Provider Dispatcher**: [`ProviderRouter.dispatch_request`](file:///c:/Projects/Nova-AI/apps/backend/app/inference/provider_router.py) hard-blocks any non-Ollama requests and verifies local daemon connectivity.
3. **Failover Safeguards**: [`FallbackEngine`](file:///c:/Projects/Nova-AI/apps/backend/app/inference/fallback.py) cannot cascade to external cloud services; failover is confined to local Ollama models.
4. **Offline Voice Default**: Default TTS profile in [`voiceSettings.ts`](file:///c:/Projects/Nova-AI/apps/frontend/src/features/voice/types/voiceSettings.ts) is `nova-offline` (Windows SAPI). Optional online Edge-TTS requires explicit user opt-in in Voice Settings.
5. **Wake Word Realism**: Explicitly classified as local Whisper transcription followed by keyword matching; acoustic neural spotting is not claimed.
6. **Piper Status**: Package is installed in `.venv-stt`, but marked unconfigured due to absence of local ONNX voice checkpoint files. Local Windows SAPI serves as the offline TTS engine.

---

## 10. Nova Voice Architecture — Young Female Voice System
As of Prompt 4, Nova AI's vocal identity is upgraded to a young, natural, professional female voice with two distinct modes:

### 1. Offline Female Voice (Default Mode)
- **Engine**: Local Windows System SAPI (`System.Speech.Synthesis`).
- **Detected Installed Voices**:
  - `Microsoft Zira Desktop` (`en-US`, Female, Adult) — Selected Default Female Voice.
  - `Microsoft David Desktop` (`en-US`, Male, Adult).
- **Youthful Tuning Parameters**:
  - Pitch: `1.08` (slightly elevated, approx +8% via SSML prosody `<prosody pitch="+8%">`).
  - Speaking Rate: `1.05` (~5% faster cadence for natural youthful pacing).
  - Volume: `100%`.
- **Network Footprint**: 100% Offline. Zero network bytes transmitted.
- **Provider Limitations**: SAPI voices are limited to those installed on the host Windows operating system. Indian-accented or multilingual SAPI voices (such as Microsoft Heera) are not pre-installed by default on standard Windows installations; English speech utilizes `Microsoft Zira Desktop`.

### 2. Neural Female Voice (Optional Online Mode)
- **Engine**: Microsoft Edge Read Aloud public endpoint (`speech.platform.bing.com` via `edge-tts`).
- **Supported Female Voices**:
  - English (India): `en-IN-NeerjaNeural` (Young Professional Female).
  - Tamil (India): `ta-IN-PallaviNeural` (Young Conversational Female).
  - Hindi (India): `hi-IN-SwaraNeural` (Young Conversational Female).
- **Zero-Cost & Privacy**: Free public service, zero billing, zero accounts, zero commercial API keys. Strictly opt-in only.
- **Network Footprint**: Connects to Microsoft public speech servers. If disconnected or offline, Nova never silently falls back to an online request.

### 3. Voice Settings & Live Preview
- **Dynamic Voice Discovery**: Queries installed SAPI voices via `GET /api/v1/voice/sapi/voices`.
- **Live Voice Preview**: Generates and plays audio preview via `POST /api/v1/voice/tts/preview`, reflecting real-time provider status (`OFFLINE — Windows SAPI` vs `ONLINE — Edge TTS`).

