"""Voice Speech-To-Text (STT) and Audio API Router.

Provides local offline speech recognition powered by faster-whisper.
"""

from typing import Optional
import os
import tempfile
import asyncio
import structlog
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from pydantic import BaseModel

logger = structlog.get_logger("voice_router")

router = APIRouter(prefix="/voice", tags=["Voice"])

# Global singleton model holder
_whisper_model = None


def _get_whisper_model(model_name: str = "tiny.en"):
    """Loads and caches local faster-whisper model in memory."""
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


class TranscribeResponse(BaseModel):
    success: bool
    transcript: str
    confidence: float = 0.95
    language: str = "en"
    duration_seconds: Optional[float] = None


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    model: str = Query("tiny.en", description="Whisper model name"),
    language: str = Query("en", description="Audio language"),
):
    """Transcribes uploaded audio file (WebM, WAV, MP3, OGG) using local faster-whisper.
    100% offline, local-first execution.
    """
    if not file:
        raise HTTPException(status_code=400, detail="Audio file must be provided.")

    contents = await file.read()
    if not contents or len(contents) < 32:
        raise HTTPException(status_code=400, detail="Audio data is empty or too small.")

    # Determine file extension from content-type or filename
    filename = file.filename or "audio.webm"
    ext = os.path.splitext(filename)[1] or ".webm"

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("wb", suffix=ext, delete=False) as tmp:
            tmp.write(contents)
            temp_path = tmp.name

        def _run_transcription():
            whisper = _get_whisper_model(model)
            segments, info = whisper.transcribe(
                temp_path,
                language=language if language != "auto" else None,
                beam_size=5,
                vad_filter=True,
            )
            text_segments = [seg.text for seg in segments]
            full_transcript = " ".join(text_segments).strip()
            confidence = float(getattr(info, "language_probability", 0.95))
            detected_lang = getattr(info, "language", language)
            duration = float(getattr(info, "duration", 0.0))
            return full_transcript, confidence, detected_lang, duration

        # Run model inference in thread pool so it does not block the async event loop
        transcript, confidence, detected_lang, duration = await asyncio.to_thread(_run_transcription)

        return TranscribeResponse(
            success=True,
            transcript=transcript,
            confidence=confidence,
            language=detected_lang,
            duration_seconds=duration,
        )
    except Exception as exc:
        logger.error("transcription_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(exc)}")
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


@router.get("/status")
async def voice_status():
    """Returns local voice STT engine readiness and configuration."""
    return {
        "status": "ready",
        "engine": "faster-whisper",
        "model": "tiny.en",
        "offline": True,
        "supported_formats": ["webm", "wav", "mp3", "ogg", "m4a"],
    }

