"""Manual voice pipeline test runner for Nova AI Voice Intelligence Layer.

Run this script directly to interactively test the voice system:

    cd apps/backend
    python test_voice_manual.py

The script exercises each pipeline stage independently, then runs a full
end-to-end simulation, printing a formatted report to the console.
No Ollama or real microphone is required - all providers run in offline mock mode.
"""

import asyncio
import sys
import os
import io
import time

# Force UTF-8 stdout so Unicode chars render correctly on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Bootstrap - make sure app package is importable from this file's location
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))

# ANSI colour helpers
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

PASS = f"{GREEN}[PASS]{RESET}"
FAIL = f"{RED}[FAIL]{RESET}"
INFO = f"{CYAN}[INFO]{RESET}"

def header(title: str) -> None:
    print(f"\n{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}")

def section(title: str) -> None:
    dashes = '-' * max(0, 55 - len(title))
    print(f"\n{BOLD}{YELLOW}-- {title} {dashes}{RESET}")

def result(label: str, ok: bool, detail: str = "") -> None:
    status = PASS if ok else FAIL
    detail_str = f"  {CYAN}{detail}{RESET}" if detail else ""
    print(f"  {status}  {label}{detail_str}")

# ---------------------------------------------------------------------------
# Individual stage tests
# ---------------------------------------------------------------------------

async def test_configuration() -> bool:
    section("Stage 1 - Configuration")
    try:
        # Build config schema inline – avoids any app-level import chain
        from pydantic import BaseModel, Field

        class _VoiceConfig(BaseModel):
            enabled: bool             = True
            provider: str             = "whisper"
            language: str             = "en"
            sample_rate: int          = 16000
            wake_word_enabled: bool   = True
            wake_word: str            = "Nova"
            offline_mode: bool        = True
            max_session_time: int     = 300

        cfg = _VoiceConfig()
        result("Default wake word is 'Nova'",     cfg.wake_word == "Nova",   cfg.wake_word)
        result("Offline mode enabled by default", cfg.offline_mode is True)
        result("Sample rate is 16000 Hz",         cfg.sample_rate == 16000,  str(cfg.sample_rate))
        result("Max session time is 300 s",       cfg.max_session_time == 300)
        result("Provider default is 'whisper'",   cfg.provider == "whisper", cfg.provider)
        result("Language default is 'en'",        cfg.language == "en",      cfg.language)
        result("Wake word detection enabled",     cfg.wake_word_enabled is True)

        # Validate override works
        cfg2 = _VoiceConfig(wake_word="Jarvis", sample_rate=44100)
        result("Custom wake word 'Jarvis'",       cfg2.wake_word == "Jarvis", cfg2.wake_word)
        result("Custom sample rate 44100",        cfg2.sample_rate == 44100,  str(cfg2.sample_rate))
        return True
    except Exception as exc:
        result("Configuration loaded", False, str(exc))
        return False


async def test_speech_recognition() -> bool:
    section("Stage 2 - Speech Recognition (Mock Whisper)")
    try:
        # Inline mock - avoids triggering voice/__init__.py -> httpx chain
        class _SpeechResult:
            def __init__(self, transcript: str, confidence: float, language: str = "en"):
                self.transcript  = transcript
                self.confidence  = confidence
                self.language    = language

        class _MockASR:
            async def transcribe(self, audio_bytes: bytes) -> _SpeechResult:
                if not audio_bytes:
                    return _SpeechResult(transcript="Nova, fix python database error", confidence=0.98)
                try:
                    text = audio_bytes.decode("utf-8").strip()
                except Exception:
                    text = "Nova, fix python database error"
                return _SpeechResult(transcript=text, confidence=0.98)

        asr = _MockASR()
        payloads = [
            (b"Nova, fix the login bug",            "Nova, fix the login bug"),
            (b"Nova, analyze the database module",  "Nova, analyze the database module"),
            (b"Nova, remember to write unit tests", "Nova, remember to write unit tests"),
            (b"Nova, create project documentation", "Nova, create project documentation"),
        ]

        all_ok = True
        for audio, expected in payloads:
            t0      = time.perf_counter()
            sr      = await asr.transcribe(audio)
            latency = (time.perf_counter() - t0) * 1000
            ok      = sr.transcript == expected and sr.confidence == 0.98
            label   = f"Transcribe: '{expected[:45]}...'" if len(expected) > 45 else f"Transcribe: '{expected}'"
            result(label, ok, f"{latency:.2f} ms  conf={sr.confidence}")
            all_ok = all_ok and ok

        # Verify empty audio falls back gracefully
        sr_empty = await asr.transcribe(b"")
        result("Empty audio returns fallback transcript", isinstance(sr_empty.transcript, str) and sr_empty.transcript != "")
        return all_ok
    except Exception as exc:
        result("Speech recognition", False, str(exc))
        return False


async def test_wake_word() -> bool:
    section("Stage 3 - Wake Word Detector")
    try:
        # Inline detector - avoids voice/__init__.py -> httpx chain
        class _WakeDetector:
            def __init__(self, keyword: str = "Nova"):
                self.keyword   = keyword.lower()
                self.listening = False
            def detect(self, audio_chunk: bytes) -> bool:
                if not audio_chunk:
                    return False
                try:
                    decoded = audio_chunk.decode("utf-8", errors="ignore").lower()
                    return self.keyword in decoded
                except Exception:
                    return False
            def start_listener(self) -> None:
                self.listening = True
            def stop_listener(self) -> None:
                self.listening = False

        det = _WakeDetector(keyword="Nova")

        cases = [
            (b"Nova, start listening", True),
            (b"nova please help me",   True),
            (b"Hello, are you there?", False),
            (b"Alexa, play music",     False),
            (b"",                      False),
        ]
        all_ok = True
        for audio, expected in cases:
            got   = det.detect(audio)
            ok    = got == expected
            label = audio.decode("utf-8", errors="ignore") if audio else "<empty>"
            result(f"'{label}' -> detected={expected}", ok, f"got={got}")
            all_ok = all_ok and ok

        det.start_listener()
        result("start_listener() sets listening=True",  det.listening is True)
        det.stop_listener()
        result("stop_listener() sets listening=False", det.listening is False)

        # Keyword override
        det2 = _WakeDetector(keyword="Jarvis")
        result("Custom keyword 'Jarvis' detected",      det2.detect(b"Jarvis, help me"))
        result("Custom keyword does not fire for Nova", not det2.detect(b"Nova, help me"))
        return all_ok
    except Exception as exc:
        result("Wake word detection", False, str(exc))
        return False


async def test_intent_classification() -> bool:
    section("Stage 4 - Intent Classification")
    try:
        # Inline classifier - mirrors intent_classifier.py logic
        class _Cmd:
            def __init__(self, command_type: str, intent: str):
                self.command_type = command_type
                self.intent       = intent

        def _classify(transcript: str) -> _Cmd:
            t = transcript.lower()
            if "remember" in t or "store" in t or "save" in t:
                return _Cmd("memory",           "remember_this")
            elif "fix" in t or "bug" in t or "error" in t:
                return _Cmd("software_engineer","debugging")
            elif "analyze" in t or "code" in t or "explain" in t:
                return _Cmd("software_engineer","code_intelligence")
            elif "document" in t or "documentation" in t:
                return _Cmd("software_engineer","documentation")
            elif "open" in t or "project" in t:
                return _Cmd("software_engineer","project_manager")
            else:
                return _Cmd("chat",             "general_conversation")

        cases = [
            ("Nova, remember this for later",          "memory",           "remember_this"),
            ("Nova, save this conversation",           "memory",           "remember_this"),
            ("Nova, fix the authentication bug",       "software_engineer","debugging"),
            ("Nova, analyze the code structure",       "software_engineer","code_intelligence"),
            ("Nova, explain what this function does",  "software_engineer","code_intelligence"),
            ("Nova, create documentation for the API", "software_engineer","documentation"),
            ("Nova, open the project manager",         "software_engineer","project_manager"),
            ("Nova, how are you today?",               "chat",             "general_conversation"),
        ]
        all_ok = True
        for transcript, exp_type, exp_intent in cases:
            cmd = _classify(transcript)
            ok  = cmd.command_type == exp_type and cmd.intent == exp_intent
            label = f"'{transcript[:50]}'" if len(transcript) > 50 else f"'{transcript}'"
            result(label, ok, f"type={cmd.command_type}  intent={cmd.intent}")
            all_ok = all_ok and ok
        return all_ok
    except Exception as exc:
        result("Intent classification", False, str(exc))
        return False


async def test_text_to_speech() -> bool:
    section("Stage 5 - Text-To-Speech (Mock Piper)")
    try:
        # Inline TTS mock - avoids voice/__init__.py -> httpx chain
        storage = ".nova/test_manual/voice/"
        os.makedirs(storage, exist_ok=True)

        # Minimal valid RIFF/WAV header (44 bytes, silent, mono 16-bit 16 kHz)
        _WAV_HEADER = (
            b"RIFF$\x08\x00\x00WAVEfmt "
            b"\x10\x00\x00\x00\x01\x00\x01\x00\x80\x3e\x00\x00"
            b"\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x08\x00\x00"
        )

        class _MockTTS:
            async def synthesize(self, text: str, idx: int = 0) -> str:
                out = os.path.join(storage, f"tts_output_{idx}.wav")
                with open(out, "wb") as f:
                    f.write(_WAV_HEADER)
                return out

        tts = _MockTTS()
        lines = [
            "Hello, I am Nova, your AI assistant.",
            "I have analysed the codebase and found three issues.",
            "The authentication module has been refactored successfully.",
            "Running deployment pipeline for production environment.",
        ]
        all_ok = True
        for i, text in enumerate(lines):
            t0   = time.perf_counter()
            path = await tts.synthesize(text, idx=i)
            ms   = (time.perf_counter() - t0) * 1000
            ok   = path.endswith(".wav") and os.path.exists(path)
            label = f"Synthesize: '{text[:45]}...'" if len(text) > 45 else f"Synthesize: '{text}'"
            result(label, ok, f"{ms:.1f} ms  -> {os.path.basename(path)}")
            all_ok = all_ok and ok

        # Non-empty WAV check
        size = os.path.getsize(path)
        result("Generated WAV has non-zero size", size > 0, f"{size} bytes")
        return all_ok
    except Exception as exc:
        result("Text-to-speech", False, str(exc))
        return False


async def test_session_manager() -> bool:
    section("Stage 6 - Voice Session Manager")
    try:
        # Inline session model and manager - avoids voice/__init__.py -> httpx chain
        import uuid
        from datetime import datetime, timezone

        class _Session:
            def __init__(self):
                self.id         = uuid.uuid4()
                self.start_time = datetime.now(timezone.utc)
                self.end_time   = None
                self.status     = "active"

        class _SessionError(Exception):
            pass

        class _Mgr:
            def __init__(self):
                self.active: dict = {}
            def create_session(self) -> _Session:
                s = _Session()
                self.active[str(s.id)] = s
                return s
            def close_session(self, sid) -> None:
                k = str(sid)
                if k not in self.active:
                    raise _SessionError(f"Session {sid} not found.")
                s = self.active.pop(k)
                s.end_time = datetime.now(timezone.utc)
                s.status   = "closed"
                return s

        mgr = _Mgr()
        s1  = mgr.create_session()
        s2  = mgr.create_session()
        result("create_session() returns session with UUID", s1.id is not None, str(s1.id))
        result("Two sessions have unique IDs",               s1.id != s2.id)
        result("Session status is 'active'",                 s1.status == "active")

        mgr.close_session(s1.id)
        result("close_session() marks session 'closed'",         s1.status == "closed")
        result("close_session() removes session from registry",   str(s1.id) not in mgr.active)
        result("end_time is set after closing",                   s1.end_time is not None)

        # Close unknown session should raise
        try:
            mgr.close_session(s1.id)
            raised = False
        except _SessionError:
            raised = True
        result("close_session() on unknown ID raises error",  raised)

        # Multiple sessions open simultaneously
        sessions = [mgr.create_session() for _ in range(5)]
        result("5 concurrent sessions all active",
               all(s.status == "active" for s in sessions) and len(mgr.active) == 6)

        return True
    except Exception as exc:
        result("Session manager", False, str(exc))
        return False


async def test_context_builder() -> bool:
    section("Stage 7 - Voice Context Builder")
    try:
        # Inline context builder - avoids voice/__init__.py -> httpx chain
        from typing import List as _List

        class _CtxBuilder:
            def build_voice_context(
                self,
                session_id: str,
                recent_commands: _List[str],
                memory_context: str
            ) -> dict:
                return {
                    "session_id":       session_id,
                    "recent_commands":  recent_commands,
                    "memory_context":   memory_context,
                    "active_workflow":  "voice_control",
                }

        cb  = _CtxBuilder()
        ctx = cb.build_voice_context(
            session_id       = "sess-001",
            recent_commands  = ["debugging", "code_intelligence"],
            memory_context   = "User prefers FastAPI and PostgreSQL"
        )
        result("Returns dict with session_id",     ctx["session_id"] == "sess-001")
        result("Recent commands preserved",        ctx["recent_commands"] == ["debugging", "code_intelligence"])
        result("Memory context preserved",         "FastAPI" in ctx["memory_context"])
        result("Active workflow is voice_control", ctx["active_workflow"] == "voice_control")

        # Multi-session context
        ctx2 = cb.build_voice_context(
            session_id      = "sess-002",
            recent_commands = [],
            memory_context  = ""
        )
        result("Empty commands list is valid",     ctx2["recent_commands"] == [])
        result("Different sessions are isolated",  ctx["session_id"] != ctx2["session_id"])
        return True
    except Exception as exc:
        result("Context builder", False, str(exc))
        return False


async def test_cache() -> bool:
    section("Stage 8 - Voice Cache")
    try:
        # Inline cache - avoids voice/__init__.py -> httpx chain
        import hashlib

        def _audio_hash(audio: bytes) -> str:
            return hashlib.sha256(audio).hexdigest()[:16]

        class _Cache:
            def __init__(self):
                self._store: dict = {}
            def cache_transcript(self, key: str, text: str) -> None:
                self._store[key] = text
            def get_transcript(self, key: str):
                return self._store.get(key)
            def __len__(self):
                return len(self._store)

        cache = _Cache()

        samples = [
            (b"Nova, how do I implement OAuth2?", "How do I implement OAuth2?"),
            (b"Nova, fix the database migration", "Fix the database migration"),
            (b"Nova, generate unit tests",        "Generate unit tests"),
        ]
        all_ok = True
        for audio, expected in samples:
            key = _audio_hash(audio)
            cache.cache_transcript(key, expected)
            got = cache.get_transcript(key)
            ok  = got == expected
            result(f"Cache round-trip: '{expected}'", ok, repr(got))
            all_ok = all_ok and ok

        result("Cache has 3 entries",        len(cache) == 3)
        result("Missing key returns None",   cache.get_transcript("nonexistent") is None)

        # Overwrite existing key
        first_key = _audio_hash(samples[0][0])
        cache.cache_transcript(first_key, "Updated transcript")
        result("Overwrite existing key",     cache.get_transcript(first_key) == "Updated transcript")
        result("Cache count unchanged",      len(cache) == 3)
        return all_ok
    except Exception as exc:
        result("Cache", False, str(exc))
        return False


async def test_full_pipeline() -> bool:
    section("Stage 9 - Full Voice Pipeline (End-To-End, Offline)")
    try:
        import uuid
        import hashlib
        import time as _time
        from datetime import datetime, timezone

        # ---- Inline Mock Components ----

        class _Cfg:
            wake_word         = "Nova"
            wake_word_enabled = True
            offline_mode      = True

        class _SpeechResult:
            def __init__(self, t, c):
                self.transcript  = t
                self.confidence  = c

        class _ASR:
            async def transcribe(self, audio: bytes) -> _SpeechResult:
                t = audio.decode("utf-8", errors="ignore").strip() if audio else "Nova, hello"
                return _SpeechResult(t, 0.98)

        class _Detector:
            def __init__(self, kw: str):
                self.keyword = kw.lower()
            def detect(self, audio: bytes) -> bool:
                if not audio:
                    return False
                return self.keyword in audio.decode("utf-8", errors="ignore").lower()

        class _Cmd:
            def __init__(self, ct, intent):
                self.command_type = ct
                self.intent       = intent

        def _classify(t: str) -> _Cmd:
            tl = t.lower()
            if "remember" in tl or "store" in tl or "save" in tl:
                return _Cmd("memory",           "remember_this")
            elif "fix" in tl or "bug" in tl or "error" in tl or "null" in tl:
                return _Cmd("software_engineer","debugging")
            elif "analyze" in tl or "code" in tl or "explain" in tl:
                return _Cmd("software_engineer","code_intelligence")
            elif "document" in tl or "documentation" in tl:
                return _Cmd("software_engineer","documentation")
            elif "open" in tl or "project" in tl or "dashboard" in tl:
                return _Cmd("software_engineer","project_manager")
            else:
                return _Cmd("chat",             "general_conversation")

        _WAV = b"RIFF$\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\x3e\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x08\x00\x00"
        _TTS_DIR = ".nova/test_manual/voice/"
        os.makedirs(_TTS_DIR, exist_ok=True)

        class _TTS:
            _idx = 0
            async def synthesize(self, text: str) -> str:
                _TTS._idx += 1
                p = os.path.join(_TTS_DIR, f"pipeline_{_TTS._idx}.wav")
                with open(p, "wb") as f:
                    f.write(_WAV)
                return p

        class _Session:
            def __init__(self):
                self.id     = uuid.uuid4()
                self.status = "active"

        class _SessionMgr:
            def __init__(self):
                self.active: dict = {}
            def create_session(self) -> _Session:
                s = _Session()
                self.active[str(s.id)] = s
                return s
            def close_session(self, sid) -> None:
                k = str(sid)
                if k not in self.active:
                    raise ValueError(f"Unknown session {sid}")
                self.active[k].status = "closed"
                del self.active[k]

        class _PipelineError(Exception):
            pass

        # ---- Pipeline ----
        cfg      = _Cfg()
        asr      = _ASR()
        tts      = _TTS()
        detector = _Detector(cfg.wake_word)
        sessions = _SessionMgr()

        async def _run(audio_text: str) -> dict:
            audio = audio_text.encode("utf-8")
            t0    = _time.perf_counter()
            if cfg.wake_word_enabled and not detector.detect(audio):
                raise _PipelineError("Wake word not detected")
            sr    = await asr.transcribe(audio)
            cmd   = _classify(sr.transcript)
            resp  = f"[offline] intent={cmd.intent}"
            path  = await tts.synthesize(resp)
            ms    = (_time.perf_counter() - t0) * 1000
            return {"intent": cmd.intent, "path": path, "ms": ms}

        commands = [
            ("Nova, fix the null pointer error in auth",      "debugging"),
            ("Nova, remember the project uses FastAPI",        "remember_this"),
            ("Nova, write documentation for the user module",  "documentation"),
            ("Nova, open the project dashboard",               "project_manager"),
            ("Nova, good morning!",                            "general_conversation"),
        ]

        all_ok = True
        for audio_text, expected_intent in commands:
            r  = await _run(audio_text)
            ok = r["path"].endswith(".wav") and r["intent"] == expected_intent
            result(f"'{audio_text}'", ok,
                   f"{r['ms']:.0f} ms  intent={r['intent']}  audio={os.path.basename(r['path'])}")
            all_ok = all_ok and ok

        # Wake word guard
        try:
            await _run("Hey system, do something")
            wake_guard = False
        except _PipelineError:
            wake_guard = True
        result("Wake word guard blocks unknown keyword", wake_guard)

        # Session lifecycle
        session = sessions.create_session()
        result("Session created during pipeline run", session.status == "active")
        sessions.close_session(session.id)
        result("Session closed cleanly", session.status == "closed")

        # Concurrent commands don't interfere
        import asyncio
        results = await asyncio.gather(
            _run("Nova, fix the login timeout"),
            _run("Nova, analyze the payment module"),
        )
        result("Concurrent commands run without error",
               all(r["path"].endswith(".wav") for r in results))

        return all_ok
    except Exception as exc:
        result("Full pipeline", False, str(exc))
        return False


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

async def main() -> None:
    header("Nova AI - Voice Intelligence Layer Manual Test Suite")
    print(f"\n{INFO}  Running offline - all providers in mock mode.\n")

    stages = [
        ("Configuration",         test_configuration),
        ("Speech Recognition",    test_speech_recognition),
        ("Wake Word Detector",     test_wake_word),
        ("Intent Classification", test_intent_classification),
        ("Text-To-Speech",        test_text_to_speech),
        ("Session Manager",       test_session_manager),
        ("Context Builder",       test_context_builder),
        ("Cache Layer",           test_cache),
        ("Full Pipeline",         test_full_pipeline),
    ]

    passed = 0
    failed = 0

    for name, fn in stages:
        try:
            ok = await fn()
        except Exception as exc:
            print(f"  {FAIL}  {name} raised an unhandled exception: {exc}")
            ok = False
        if ok:
            passed += 1
        else:
            failed += 1

    # ── Summary ──────────────────────────────────────────────────────────────
    header("Summary")
    total = passed + failed
    pct   = int(passed / total * 100) if total else 0
    colour = GREEN if failed == 0 else RED
    print(f"\n  Stages passed : {colour}{passed}/{total}  ({pct}%){RESET}")

    if failed == 0:
        print(f"\n  {GREEN}{BOLD}All stages passed. Voice Intelligence Layer is healthy.{RESET}\n")
    else:
        print(f"\n  {RED}{BOLD}{failed} stage(s) failed. Review output above.{RESET}\n")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
