"""Voice Speech-To-Text (STT), Multilingual Intelligence, Wake-Word Detection,
and Text-To-Speech (TTS) API Router for Nova OS 2.0.

Provides offline multilingual speech recognition (English, Tamil, Hindi, Code-Switching)
powered by faster-whisper and dedicated Nova Indian Professional voice management.
"""

from typing import Optional, List, Dict, Any, Tuple
import os
import tempfile
import asyncio
import subprocess
import json
import structlog
from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Response
from pydantic import BaseModel, Field

from app.ai.voice.stt_engine import LocalSTTEngine
from app.ai.voice.conversational.wake_word import ConversationalWakeWordEngine

logger = structlog.get_logger("voice_router")

router = APIRouter(prefix="/voice", tags=["Voice"])

# Global singleton model holders
_whisper_model = None
_stt_engine = None


def _get_stt_engine() -> LocalSTTEngine:
    global _stt_engine
    if _stt_engine is None:
        _stt_engine = LocalSTTEngine()
    return _stt_engine


def _get_whisper_model(model_name: str = "tiny"):
    """Loads and caches local faster-whisper model in memory if direct import is supported."""
    global _whisper_model
    if _whisper_model is None:
        import av
        # Patch av.open to ignore metadata_errors if newer PyAV is present
        _orig_av_open = av.open

        def _safe_av_open(*args, **kwargs):
            kwargs.pop("metadata_errors", None)
            return _orig_av_open(*args, **kwargs)

        av.open = _safe_av_open

        from faster_whisper import WhisperModel
        logger.info("loading_whisper_model", model=model_name)
        _whisper_model = WhisperModel(model_name, device="cpu", compute_type="int8")
        logger.info("whisper_model_loaded", model=model_name)
    return _whisper_model


async def _transcribe_payload(
    contents: bytes,
    filename: str = "audio.webm",
    model: str = "tiny",
    language: Optional[str] = None
):
    """Transcribes audio contents using either direct in-memory WhisperModel or isolated LocalSTTEngine."""
    target_lang = language if language and language != "auto" else None
    target_model = model

    # If Tamil or Hindi requested on an English-only model, switch to multilingual tiny
    if target_lang in ["ta", "hi"] and target_model.endswith(".en"):
        target_model = "tiny"

    try:
        # First attempt direct faster-whisper in-memory execution
        ext = os.path.splitext(filename)[1] or ".webm"
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile("wb", suffix=ext, delete=False) as tmp:
                tmp.write(contents)
                temp_path = tmp.name

            def _run_transcription():
                whisper = _get_whisper_model(target_model)
                segments, info = whisper.transcribe(
                    temp_path,
                    language=target_lang,
                    beam_size=5,
                    vad_filter=True,
                )
                text_segments = [seg.text for seg in segments]
                full_transcript = " ".join(text_segments).strip()
                confidence = float(getattr(info, "language_probability", 0.95))
                detected_lang = getattr(info, "language", target_lang or "en")
                duration = float(getattr(info, "duration", 0.0))
                return full_transcript, confidence, detected_lang, duration

            return await asyncio.to_thread(_run_transcription)
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
    except (ImportError, ModuleNotFoundError):
        # Fall back to isolated LocalSTTEngine (.venv-stt)
        stt = _get_stt_engine()
        result = await stt.transcribe(contents, language=target_lang)
        return result.transcript, result.confidence, result.language, 0.0


# --------------------------------------------------------------------------
# Request & Response Models
# --------------------------------------------------------------------------

class TranscribeResponse(BaseModel):
    success: bool
    transcript: str
    confidence: float = 0.95
    language: str = "en"
    language_probability: float = 0.95
    duration_seconds: Optional[float] = None


class WakeWordDetectResponse(BaseModel):
    detected: bool
    keyword: str = ""
    confidence: float = 0.0
    stripped_command: str = ""
    raw_transcript: str = ""


class CheckTextWakeWordRequest(BaseModel):
    text: str
    keywords: Optional[List[str]] = None


class WakeWordConfigResponse(BaseModel):
    default_wake_phrase: str = "Hey Nova"
    supported_keywords: List[str] = ["hey nova", "nova", "jarvis", "computer"]
    offline: bool = True
    provider: str = "local_whisper_keyword_matcher"
    engine_mechanism: str = "faster_whisper_transcription_plus_keyword_matching"
    is_dedicated_acoustic_engine: bool = False
    notes: str = (
        "Operates via local faster-whisper audio transcription followed by lexical keyword spotting. "
        "Does not utilize a raw acoustic neural feature spotter."
    )


class SynthesizeSpeechRequest(BaseModel):
    text: str
    language: Optional[str] = "en-IN"
    profile: Optional[str] = "nova-offline-female"
    pitch: Optional[float] = 1.08
    rate: Optional[float] = 1.05


class GenerateSpeechRequest(BaseModel):
    text: str
    language: Optional[str] = "en-IN"
    voice: Optional[str] = None
    profile: Optional[str] = "nova-offline-female"
    mode: Optional[str] = "offline"  # "offline" (Windows SAPI) or "neural" (Edge TTS)
    pitch: Optional[float] = 1.08    # Youthful elevated female pitch default (+8%)
    rate: Optional[float] = 1.05     # Youthful natural speed default (+5%)
    volume: Optional[float] = 100.0
    offline_only: Optional[bool] = False
    prefer_offline: Optional[bool] = False


class PreviewSpeechRequest(BaseModel):
    text: Optional[str] = None
    language: Optional[str] = "en-IN"
    voice: Optional[str] = None
    mode: Optional[str] = "offline"  # "offline" or "neural"
    pitch: Optional[float] = 1.08
    rate: Optional[float] = 1.05
    volume: Optional[float] = 100.0


# --------------------------------------------------------------------------
# API Endpoints
# --------------------------------------------------------------------------

@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    model: str = Query("tiny", description="Whisper model name: tiny (multilingual) or tiny.en"),
    language: Optional[str] = Query(None, description="Audio language: 'en', 'ta', 'hi', or None for auto-detect"),
):
    """Transcribes uploaded audio file (WebM, WAV, MP3, OGG) using local faster-whisper.
    Supports English, Tamil, Hindi, and multilingual code-switching.
    100% offline, local-first execution.
    """
    if not file:
        raise HTTPException(status_code=400, detail="Audio file must be provided.")

    contents = await file.read()
    if not contents or len(contents) < 32:
        raise HTTPException(status_code=400, detail="Audio data is empty or too small.")

    filename = file.filename or "audio.webm"

    try:
        transcript, confidence, detected_lang, duration = await _transcribe_payload(
            contents, filename=filename, model=model, language=language
        )
        return TranscribeResponse(
            success=True,
            transcript=transcript,
            confidence=confidence,
            language=detected_lang,
            language_probability=confidence,
            duration_seconds=duration,
        )
    except Exception as exc:
        logger.error("transcription_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(exc)}")


@router.post("/wake-word/detect", response_model=WakeWordDetectResponse)
async def detect_wake_word_audio(
    file: UploadFile = File(...),
    wake_phrase: Optional[str] = Query("hey nova", description="Configured wake phrase to match"),
    model: str = Query("tiny", description="Whisper model name for fast keyword spotting"),
):
    """Evaluates short audio chunk for wake keyword presence.
    100% local, offline detection.
    Returns whether wake word was detected, the keyword matched, and any trailing command.
    """
    if not file:
        raise HTTPException(status_code=400, detail="Audio file must be provided.")

    contents = await file.read()
    if not contents or len(contents) < 32:
        return WakeWordDetectResponse(detected=False)

    filename = file.filename or "audio.webm"

    # Configure wake engine with target keywords
    configured_keywords = [wake_phrase.lower().strip()]
    if "nova" not in configured_keywords and "hey nova" in configured_keywords:
        configured_keywords.append("nova")
    wake_engine = ConversationalWakeWordEngine(keywords=configured_keywords)

    try:
        raw_transcript, conf, _, _ = await _transcribe_payload(
            contents, filename=filename, model=model, language=None
        )
        if not raw_transcript:
            return WakeWordDetectResponse(detected=False)

        detected, stripped_cmd, event = wake_engine.check_activation(text=raw_transcript)
        return WakeWordDetectResponse(
            detected=detected,
            keyword=event.keyword if event else (configured_keywords[0] if detected else ""),
            confidence=event.confidence if event else (conf if detected else 0.0),
            stripped_command=stripped_cmd or "",
            raw_transcript=raw_transcript,
        )
    except Exception as exc:
        logger.warning("wake_word_audio_detection_failed", error=str(exc))
        return WakeWordDetectResponse(detected=False)


@router.post("/wake-word/check-text", response_model=WakeWordDetectResponse)
async def check_wake_word_text(request: CheckTextWakeWordRequest):
    """Fast check whether text begins with or contains wake phrase and strips the prefix."""
    text = request.text.strip()
    if not text:
        return WakeWordDetectResponse(detected=False)

    keywords = [k.lower().strip() for k in (request.keywords or ["hey nova", "nova"])]
    wake_engine = ConversationalWakeWordEngine(keywords=keywords)
    detected, stripped_cmd, event = wake_engine.check_activation(text=text)

    return WakeWordDetectResponse(
        detected=detected,
        keyword=event.keyword if event else (keywords[0] if detected else ""),
        confidence=1.0 if detected else 0.0,
        stripped_command=stripped_cmd or "",
        raw_transcript=text,
    )


@router.get("/wake-word/config", response_model=WakeWordConfigResponse)
async def get_wake_word_config():
    """Returns local wake-word detector capabilities and default keywords."""
    return WakeWordConfigResponse()


@router.get("/languages")
async def get_supported_languages():
    """Returns multilingual capabilities and priority language support matrix."""
    return {
        "priority_languages": [
            {
                "code": "auto",
                "name": "Auto-Detect (Multilingual Code-Switching)",
                "locales": ["en-IN", "ta-IN", "hi-IN"],
                "supported": True,
            },
            {
                "code": "en",
                "name": "English (Indian Professional)",
                "locales": ["en-IN", "en-US", "en-GB"],
                "supported": True,
            },
            {
                "code": "ta",
                "name": "Tamil (தமிழ்)",
                "locales": ["ta-IN"],
                "supported": True,
            },
            {
                "code": "hi",
                "name": "Hindi (हिन्दी)",
                "locales": ["hi-IN"],
                "supported": True,
            },
        ],
        "active_stt_engine": "faster-whisper",
        "active_voice_profile": "NOVA — Indian Professional",
        "code_switching_supported": True,
        "offline": True,
    }


_cached_sapi_voices = None


async def _get_installed_sapi_voices_cached() -> List[Dict[str, Any]]:
    """Dynamically queries and caches installed Windows SAPI voices with metadata."""
    global _cached_sapi_voices
    if _cached_sapi_voices is not None:
        return _cached_sapi_voices

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    venv_python = os.path.join(base_dir, ".venv-stt", "Scripts", "python.exe")
    worker_script = os.path.join(base_dir, "app", "ai", "voice", "text_to_speech", "isolated_tts_worker.py")

    def _query():
        if os.path.exists(venv_python) and os.path.exists(worker_script):
            res = subprocess.run(
                [venv_python, worker_script, "--list-sapi-voices"],
                capture_output=True,
                text=True,
                timeout=12,
            )
            if res.returncode == 0 and res.stdout.strip():
                try:
                    return json.loads(res.stdout)
                except Exception:
                    pass
        return [
            {
                "name": "Microsoft Zira Desktop",
                "culture": "en-US",
                "gender": "Female",
                "age": "Adult",
                "description": "Microsoft Zira Desktop - English (United States)",
                "is_female": True,
                "is_default": True,
            }
        ]

    voices = await asyncio.to_thread(_query)
    _cached_sapi_voices = voices
    return voices


async def _synthesize_audio_payload(
    text: str,
    language: str = "en-IN",
    voice: Optional[str] = None,
    pitch: float = 1.08,
    rate: float = 1.05,
    volume: float = 100.0,
    offline_only: bool = False,
    prefer_offline: bool = False,
) -> Tuple[bytes, str, str, str]:
    """Synthesizes real audible audio payload using isolated worker or SAPI fallback.
    Returns (audio_bytes, media_type, voice_used, engine_used).
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    venv_python = os.path.join(base_dir, ".venv-stt", "Scripts", "python.exe")
    worker_script = os.path.join(base_dir, "app", "ai", "voice", "text_to_speech", "isolated_tts_worker.py")

    ext = ".mp3" if not (offline_only or prefer_offline) else ".wav"
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("wb", suffix=ext, delete=False) as tmp:
            temp_path = tmp.name

        def _run_worker() -> Tuple[bytes, str, str, str]:
            # 1. Try isolated worker with EdgeTTS / local worker
            if os.path.exists(venv_python) and os.path.exists(worker_script):
                cmd = [
                    venv_python,
                    worker_script,
                    "--text", text,
                    "--output", temp_path,
                    "--language", language,
                    "--rate", str(rate),
                    "--pitch", str(pitch),
                    "--volume", str(volume),
                ]
                if voice:
                    cmd.extend(["--voice", voice])
                if offline_only:
                    cmd.append("--offline-only")
                elif prefer_offline:
                    cmd.append("--prefer-offline")

                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
                if proc.returncode == 0 and os.path.exists(temp_path) and os.path.getsize(temp_path) > 100:
                    with open(temp_path, "rb") as f:
                        data = f.read()

                    voice_used = voice or ("Microsoft Zira Desktop" if (offline_only or prefer_offline) else "en-IN-NeerjaNeural")
                    engine_used = "windows-sapi" if (offline_only or prefer_offline) else "edge-tts"
                    try:
                        for line in proc.stdout.splitlines():
                            if line.strip().startswith("{") and line.strip().endswith("}"):
                                parsed = json.loads(line)
                                voice_used = parsed.get("voice", voice_used)
                                engine_used = parsed.get("engine", engine_used)
                                break
                    except Exception:
                        pass

                    media_type = "audio/mpeg" if temp_path.endswith(".mp3") else "audio/wav"
                    return data, media_type, voice_used, engine_used

            # 2. Local Windows System.Speech SAPI Fallback (100% offline, Female Voice Priority)
            escaped = text.replace("'", "''")
            wav_fallback = os.path.splitext(temp_path)[0] + "_sapi.wav"
            target_voice_arg = (voice or "").replace("'", "''")
            ps_script = (
                "Add-Type -AssemblyName System.Speech; "
                "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                f"$target = '{target_voice_arg}'; "
                "$installed = $synth.GetInstalledVoices() | Select-Object -ExpandProperty VoiceInfo; "
                "if ($target) { "
                "  $matched = $installed | Where-Object { $_.Name -like \"*$target*\" } | Select-Object -First 1; "
                "  if ($matched) { $synth.SelectVoice($matched.Name) } "
                "} else { "
                "  $female = $installed | Where-Object { $_.Gender -eq [System.Speech.Synthesis.VoiceGender]::Female -or $_.Name -match 'Zira|Heera' } | Select-Object -First 1; "
                "  if ($female) { $synth.SelectVoice($female.Name) } "
                "}; "
                "$synth.Rate = 1; "
                "$synth.Volume = 100; "
                f"$synth.SetOutputToWaveFile('{wav_fallback}'); "
                f"$synth.Speak('{escaped}'); "
                "$vUsed = if ($synth.Voice) { $synth.Voice.Name } else { 'windows-sapi' }; "
                "$synth.Dispose(); "
                "Write-Output \"VOICE_USED:$vUsed\";"
            )
            res = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if res.returncode == 0 and os.path.exists(wav_fallback) and os.path.getsize(wav_fallback) > 100:
                with open(wav_fallback, "rb") as f:
                    data = f.read()
                try:
                    os.remove(wav_fallback)
                except Exception:
                    pass
                actual_v = "Microsoft Zira Desktop"
                for line in res.stdout.splitlines():
                    if line.strip().startswith("VOICE_USED:"):
                        actual_v = line.strip().split("VOICE_USED:", 1)[1].strip()
                        break
                return data, "audio/wav", actual_v, "windows-sapi"

            raise RuntimeError("Audio synthesis failed across all local providers.")

        return await asyncio.to_thread(_run_worker)
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


@router.get("/sapi/voices")
async def get_sapi_voices():
    """Returns dynamically detected installed Windows SAPI voices with metadata."""
    return await _get_installed_sapi_voices_cached()


@router.get("/tts/voices")
async def get_tts_voice_profiles():
    """Returns voice profiles and dynamic installed voices with full cost transparency."""
    installed_sapi = await _get_installed_sapi_voices_cached()
    return {
        "zero_cost_policy": {
            "guarantee": "100% Free - Zero Paid APIs, Zero Subscriptions, Zero Commercial Billing",
            "enforced": True,
            "offline_core_supported": True,
        },
        "voice_modes": [
            {
                "id": "offline_female",
                "name": "Offline Female Voice (Windows SAPI)",
                "description": "Default local-first offline voice using installed Windows SAPI voices. Operates completely without internet.",
                "is_default": True,
                "is_offline": True,
                "is_online": False,
                "status": "OFFLINE",
                "default_voice": "Microsoft Zira Desktop",
                "installed_voices": installed_sapi,
            },
            {
                "id": "neural_female",
                "name": "Neural Female Voice (Edge TTS)",
                "description": "Optional online high-definition neural female voice via Microsoft Edge. Free public service, zero billing, zero API keys.",
                "is_default": False,
                "is_offline": False,
                "is_online": True,
                "status": "ONLINE",
                "voices": {
                    "en-IN": "en-IN-NeerjaNeural",
                    "ta-IN": "ta-IN-PallaviNeural",
                    "hi-IN": "hi-IN-SwaraNeural",
                },
            },
        ],
        "default_mode": "offline_female",
        "default_profile": "nova-offline-female",
        "default_voice": "Microsoft Zira Desktop",
        "primary_offline_engine": "windows-sapi",
        "optional_online_engine": "edge-tts",
        "local_synthesis_ready": True,
        "offline_preferred": True,
        "piper_status": "unconfigured_no_voice_models_installed",
        "installed_sapi_voices": installed_sapi,
        "profiles": [
            {
                "id": "nova-offline-female",
                "name": "NOVA — Offline Female (Windows SAPI)",
                "locale": "en-US",
                "voice_model": "Microsoft Zira Desktop",
                "gender": "female",
                "mode": "offline",
                "pitch": 1.08,
                "rate": 1.05,
                "is_offline": True,
                "is_online": False,
                "requires_internet": False,
                "requires_account": False,
                "cost": "$0.00",
                "description": "Natural youthful female voice using local Windows SAPI (Microsoft Zira Desktop). 100% offline, zero internet.",
            },
            {
                "id": "nova-neural-female-en",
                "name": "NOVA — Neural Female (Indian English Neerja)",
                "locale": "en-IN",
                "voice_model": "en-IN-NeerjaNeural",
                "gender": "female",
                "mode": "neural",
                "pitch": 1.0,
                "rate": 1.05,
                "is_offline": False,
                "is_online": True,
                "requires_internet": True,
                "requires_account": False,
                "cost": "$0.00",
                "description": "Young, natural Indian English female voice (Optional online service).",
            },
            {
                "id": "nova-neural-female-ta",
                "name": "NOVA — Neural Female (Tamil Pallavi)",
                "locale": "ta-IN",
                "voice_model": "ta-IN-PallaviNeural",
                "gender": "female",
                "mode": "neural",
                "pitch": 1.0,
                "rate": 1.05,
                "is_offline": False,
                "is_online": True,
                "requires_internet": True,
                "requires_account": False,
                "cost": "$0.00",
                "description": "Young, natural Tamil female voice with Tanglish fluency (Optional online service).",
            },
            {
                "id": "nova-neural-female-hi",
                "name": "NOVA — Neural Female (Hindi Swara)",
                "locale": "hi-IN",
                "voice_model": "hi-IN-SwaraNeural",
                "gender": "female",
                "mode": "neural",
                "pitch": 1.0,
                "rate": 1.05,
                "is_offline": False,
                "is_online": True,
                "requires_internet": True,
                "requires_account": False,
                "cost": "$0.00",
                "description": "Young, natural Hindi female voice with Hinglish fluency (Optional online service).",
            },
            {
                "id": "nova-offline",
                "name": "NOVA — Offline Local Synthesizer (SAPI)",
                "locale": "en-US",
                "voice_model": "windows-sapi",
                "gender": "female",
                "mode": "offline",
                "pitch": 1.08,
                "rate": 1.05,
                "is_offline": True,
                "is_online": False,
                "requires_internet": False,
                "requires_account": False,
                "cost": "$0.00",
                "description": "100% offline local Windows system speech synthesizer. Zero network dependency.",
            },
        ],
    }


@router.post("/tts/generate")
async def generate_speech_audio(request: GenerateSpeechRequest):
    """Synthesizes genuine audible speech and returns real audio stream.
    Supports Offline Female (Windows SAPI) and Neural Female (Edge-TTS).
    Zero fake audio. Zero paid dependencies.
    """
    clean_text = request.text.strip()
    if not clean_text:
        raise HTTPException(status_code=400, detail="Text must not be empty.")

    is_offline = True
    if request.mode == "neural" and not request.offline_only:
        is_offline = False
    elif request.mode == "offline" or request.offline_only or request.prefer_offline:
        is_offline = True
    elif request.voice and "Neural" in request.voice and not request.offline_only:
        is_offline = False

    try:
        audio_bytes, media_type, voice_used, engine_used = await _synthesize_audio_payload(
            text=clean_text,
            language=request.language or "en-IN",
            voice=request.voice,
            pitch=request.pitch or 1.08,
            rate=request.rate or 1.05,
            volume=request.volume or 100.0,
            offline_only=is_offline,
            prefer_offline=is_offline,
        )

        ext = ".mp3" if media_type == "audio/mpeg" else ".wav"
        mode_str = "offline" if engine_used == "windows-sapi" else "online"
        return Response(
            content=audio_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f"inline; filename=nova_speech{ext}",
                "X-Voice-Profile": voice_used,
                "X-TTS-Engine": engine_used,
                "X-TTS-Mode": mode_str,
                "X-Detected-Language": request.language or "en-IN",
                "X-Zero-Cost": "true",
                "X-Offline-Local": "true" if engine_used == "windows-sapi" else "false",
                "Cache-Control": "no-cache",
            },
        )
    except Exception as exc:
        logger.error("tts_generation_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {str(exc)}")


@router.post("/tts/preview")
async def preview_speech_audio(request: PreviewSpeechRequest):
    """Generates actual speech preview using the requested provider, voice, and parameters."""
    lang = request.language or "en-IN"
    sample_text = request.text
    if not sample_text or not sample_text.strip():
        if lang.startswith("ta"):
            sample_text = "வணக்கம், நான் நோவா. உங்களுக்கு எவ்வாறு உதவ முடியும்?"
        elif lang.startswith("hi"):
            sample_text = "नमस्ते, मैं नोவா हूँ। मैं आपकी क्या मदद कर सकती हूँ?"
        else:
            sample_text = "Good morning, sir. I am Nova. How may I assist you today?"

    is_offline = request.mode != "neural"
    return await generate_speech_audio(
        GenerateSpeechRequest(
            text=sample_text,
            language=lang,
            voice=request.voice,
            mode=request.mode,
            pitch=request.pitch or 1.08,
            rate=request.rate or 1.05,
            volume=request.volume or 100.0,
            offline_only=is_offline,
            prefer_offline=is_offline,
        )
    )
    except Exception as exc:
        logger.error("tts_generation_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {str(exc)}")


@router.get("/tts/generate")
async def generate_speech_audio_get(
    text: str = Query(..., description="Text to synthesize"),
    language: str = Query("en-IN", description="Language code (en-IN, ta-IN, hi-IN)"),
    voice: Optional[str] = Query(None, description="Voice model name"),
    pitch: float = Query(0.92, description="Pitch factor"),
    rate: float = Query(1.0, description="Rate factor"),
    offline_only: bool = Query(False, description="Force offline synthesis"),
):
    """GET endpoint for direct streaming into HTML5 Audio element."""
    return await generate_speech_audio(
        GenerateSpeechRequest(
            text=text,
            language=language,
            voice=voice,
            pitch=pitch,
            rate=rate,
            offline_only=offline_only,
        )
    )


@router.post("/tts/synthesize")
async def synthesize_speech(request: SynthesizeSpeechRequest):
    """Legacy metadata synthesis endpoint for compatibility."""
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text must not be empty.")

    return {
        "success": True,
        "profile": request.profile,
        "language": request.language,
        "pitch": request.pitch,
        "rate": request.rate,
        "char_count": len(request.text),
        "status": "ready_for_audio_stream",
        "audio_stream_endpoint": "/api/v1/voice/tts/generate",
    }


@router.get("/status")
async def voice_status():
    """Returns local voice STT, wake-word, and multilingual engine readiness."""
    return {
        "status": "ready",
        "engine": "faster-whisper",
        "model": "tiny",
        "offline": True,
        "multilingual": True,
        "supported_languages": ["en", "ta", "hi", "auto"],
        "voice_profile": "NOVA — Indian Professional",
        "wake_word_supported": True,
        "default_wake_phrase": "Hey Nova",
        "supported_formats": ["webm", "wav", "mp3", "ogg", "m4a"],
    }
