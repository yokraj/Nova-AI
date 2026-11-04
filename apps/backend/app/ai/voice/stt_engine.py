"""Local Offline Speech-To-Text (STT) Engine for Nova-AI Voice System.

Uses an isolated Python 3.11 environment (.venv-stt) with faster-whisper.
Enforces zero-cloud execution, local availability checking, and strict validation.
"""

from typing import Optional, Dict, Any
import os
import sys
import json
import tempfile
import subprocess
import structlog

from app.ai.voice.interfaces import ISpeechRecognizer
from app.ai.voice.models import SpeechResult
from app.ai.voice.exceptions import SpeechRecognitionError

logger = structlog.get_logger("stt_engine")


class LocalSTTEngine(ISpeechRecognizer):
    """Local offline STT engine using isolated Whisper (.venv-stt) with strict offline enforcement."""

    def __init__(
        self,
        allow_cloud: bool = False,
        model_name: str = "tiny.en",
        venv_python: Optional[str] = None,
    ) -> None:
        if allow_cloud:
            raise ValueError("Cloud STT providers are strictly forbidden in Nova offline voice system.")

        self.model_name = model_name
        self.is_offline = True

        # Resolve isolated STT Python environment path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.venv_python = venv_python or os.path.join(base_dir, ".venv-stt", "Scripts", "python.exe")
        self.worker_script = os.path.join(
            base_dir, "app", "ai", "voice", "speech_recognition", "isolated_whisper_worker.py"
        )

    def is_available(self) -> bool:
        """Checks if local STT environment or direct faster-whisper package is available."""
        try:
            import faster_whisper
            return True
        except ImportError:
            return os.path.exists(self.venv_python) and os.path.exists(self.worker_script)

    async def transcribe(self, audio_bytes: bytes, language: Optional[str] = None) -> SpeechResult:
        """Transcribes incoming audio bytes using local faster-whisper model.
        Supports multilingual transcription ('en', 'ta', 'hi', or auto).
        
        Raises SpeechRecognitionError if audio input is empty, corrupted, or transcription fails.
        No fake success.
        """
        if not audio_bytes or len(audio_bytes) < 8:
            raise SpeechRecognitionError("Audio input bytes cannot be empty or corrupted.")

        if not self.is_available():
            raise SpeechRecognitionError(
                f"Local STT engine not available and isolated STT environment not found at '{self.venv_python}'."
            )

        with tempfile.NamedTemporaryFile("wb", suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_wav = f.name

        target_model = self.model_name
        target_lang = language if language and language != "auto" else None
        if target_lang in ["ta", "hi"] and target_model.endswith(".en"):
            target_model = "tiny"

        try:
            # 1. Attempt direct faster-whisper execution first (fastest, zero-subprocess)
            try:
                import av
                _orig_av_open = av.open
                def _safe_av_open(*args, **kwargs):
                    kwargs.pop("metadata_errors", None)
                    return _orig_av_open(*args, **kwargs)
                av.open = _safe_av_open

                from faster_whisper import WhisperModel
                import asyncio

                def _run_whisper():
                    model = WhisperModel(target_model, device="cpu", compute_type="int8")
                    segments, info = model.transcribe(temp_wav, language=target_lang, beam_size=5, vad_filter=True)
                    text = " ".join([seg.text for seg in segments]).strip()
                    conf = float(getattr(info, "language_probability", 0.95))
                    lang = str(getattr(info, "language", target_lang or "en"))
                    return text, conf, lang

                transcript, confidence, lang_code = await asyncio.to_thread(_run_whisper)
                if not transcript:
                    raise SpeechRecognitionError("No speech transcribed from audio sample.")

                return SpeechResult(
                    transcript=transcript,
                    confidence=confidence,
                    language=lang_code,
                )
            except ImportError:
                pass

            # 2. Fall back to isolated worker script if direct import was unavailable
            cmd = [
                self.venv_python,
                self.worker_script,
                "--audio",
                temp_wav,
                "--model",
                target_model,
            ]
            if target_lang:
                cmd.extend(["--language", target_lang])
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if proc.returncode != 0:
                err_msg = proc.stderr.strip() or proc.stdout.strip()
                raise SpeechRecognitionError(f"STT worker process error: {err_msg}")

            stdout_text = proc.stdout.strip()
            # Find JSON payload in output
            json_line = None
            for line in stdout_text.splitlines():
                if line.startswith("{") and line.endswith("}"):
                    json_line = line
                    break

            if not json_line:
                raise SpeechRecognitionError(f"Invalid output from STT worker: {stdout_text}")

            data = json.loads(json_line)
            if "error" in data:
                raise SpeechRecognitionError(f"Whisper recognition failed: {data['error']}")

            transcript = data.get("transcript", "").strip()
            if not transcript:
                raise SpeechRecognitionError("No speech transcribed from audio sample.")

            return SpeechResult(
                transcript=transcript,
                confidence=float(data.get("confidence", 0.95)),
                language=str(data.get("language", "en")),
            )
        except SpeechRecognitionError:
            raise
        except Exception as err:
            logger.error("stt_transcription_failed", error=str(err))
            raise SpeechRecognitionError(f"Local STT transcription error: {err}")
        finally:
            if os.path.exists(temp_wav):
                try:
                    os.remove(temp_wav)
                except Exception:
                    pass
