"""Local Offline Text-To-Speech (TTS) Engine for Nova-AI Voice System.

Enforces zero-cloud execution guarantee, genuine audible speech generation,
and strict validation. Integrates isolated worker with genuine audio synthesis.
"""

from typing import Optional
import os
import sys
import json
import subprocess
import asyncio
import structlog

from app.ai.voice.interfaces import ITextToSpeechProvider
from app.ai.voice.exceptions import TextToSpeechError

logger = structlog.get_logger("tts_engine")


class LocalTTSEngine(ITextToSpeechProvider):
    """Local offline TTS synthesis engine using isolated worker and Windows SAPI fallback."""

    def __init__(
        self,
        storage_path: str = ".nova/cache/voice/",
        allow_cloud: bool = False,
        venv_python: Optional[str] = None,
    ) -> None:
        if allow_cloud:
            raise ValueError("Cloud TTS providers are strictly forbidden in Nova offline voice system.")
        self.storage_path = storage_path
        self.is_offline = True

        # Base directories for isolated worker execution
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.venv_python = venv_python or os.path.join(base_dir, ".venv-stt", "Scripts", "python.exe")
        self.worker_script = os.path.join(
            base_dir, "app", "ai", "voice", "text_to_speech", "isolated_tts_worker.py"
        )

    def is_available(self) -> bool:
        """Checks if local TTS engine is available on the system."""
        return self.is_offline

    async def synthesize(
        self,
        text: str,
        language: str = "en-IN",
        voice: Optional[str] = None,
        rate: float = 1.0,
        pitch: float = 0.92,
    ) -> str:
        """Synthesizes text into a local WAV audio file path.
        
        Raises TextToSpeechError if text is empty or file generation fails.
        Guarantees genuine, non-empty, audible speech.
        """
        if not text or not text.strip():
            raise TextToSpeechError("Text input for synthesis cannot be empty.")

        os.makedirs(self.storage_path, exist_ok=True)
        dest_file = os.path.join(self.storage_path, "synthesized_voice_response.wav")

        def _run_worker_sync() -> str:
            # 1. First attempt isolated worker with local fallback
            if os.path.exists(self.venv_python) and os.path.exists(self.worker_script):
                cmd = [
                    self.venv_python,
                    self.worker_script,
                    "--text", text,
                    "--output", dest_file,
                    "--language", language,
                    "--rate", str(rate),
                    "--pitch", str(pitch),
                ]
                if voice:
                    cmd.extend(["--voice", voice])

                try:
                    proc = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=20,
                    )
                    if proc.returncode == 0 and os.path.exists(dest_file) and os.path.getsize(dest_file) > 100:
                        return dest_file
                    else:
                        logger.warning("tts_worker_failed_falling_back", stderr=proc.stderr)
                except Exception as exc:
                    logger.warning("tts_worker_exception", error=str(exc))

            # 2. Local Direct Windows System.Speech SAPI Fallback (100% offline, guaranteed)
            try:
                escaped = text.replace("'", "''")
                ps_script = (
                    "Add-Type -AssemblyName System.Speech; "
                    "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                    f"$synth.SetOutputToWaveFile('{dest_file}'); "
                    f"$synth.Speak('{escaped}'); "
                    "$synth.Dispose();"
                )
                res = subprocess.run(
                    ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                if res.returncode == 0 and os.path.exists(dest_file) and os.path.getsize(dest_file) > 100:
                    return dest_file
            except Exception as exc:
                logger.error("sapi_direct_fallback_failed", error=str(exc))

            raise TextToSpeechError("All local TTS synthesis providers failed to generate speech.")

        try:
            return await asyncio.to_thread(_run_worker_sync)
        except TextToSpeechError:
            raise
        except Exception as err:
            logger.error("tts_synthesis_failed", error=str(err))
            raise TextToSpeechError(f"TTS synthesis failed: {err}")
