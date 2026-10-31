"""Streaming Audio Receiver and Microphone Stream Handler for Nova-AI (Phase 10M-B).

Provides streaming microphone chunk ingestion, frame slicing, speech utterance buffering,
and mandatory privacy controls with an explicit hardware/software kill-switch.
"""

from collections import deque
from typing import Callable, Deque, Dict, List, Optional
import io
import struct
import wave
import structlog

from app.ai.voice.conversational.models import AudioFrame, MicrophoneStatus, VADState
from app.ai.voice.conversational.vad import VoiceActivityDetector

logger = structlog.get_logger("conversational_audio_stream")


class StreamingAudioReceiver:
    """Ingests streaming microphone PCM chunks, runs VAD, buffers speech utterances, and enforces privacy."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        sampwidth: int = 2,
        frame_duration_ms: int = 20,
        vad: Optional[VoiceActivityDetector] = None,
        max_utterance_sec: float = 15.0,
    ) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.sampwidth = sampwidth
        self.frame_duration_ms = frame_duration_ms
        self.frame_bytes = int((sample_rate * frame_duration_ms) / 1000) * sampwidth * channels
        self.max_utterance_bytes = int(sample_rate * max_utterance_sec * sampwidth * channels)

        self.vad = vad or VoiceActivityDetector(sample_rate=sample_rate, frame_duration_ms=frame_duration_ms)

        # Privacy & Activation Controls
        self._is_active = True
        self._is_muted = False
        self._frames_processed = 0

        # Pre-roll ring buffer (preserves ~160ms pre-speech consonants)
        self._preroll_buffer: Deque[bytes] = deque(maxlen=8)
        # Active speech accumulator
        self._speech_buffer = bytearray()
        self._leftover_chunk = bytearray()

        # Telemetry
        self._latest_rms = 0.0
        self._latest_db = -100.0

    # --------------------------------------------------------------------------
    # Privacy & Hardware Controls
    # --------------------------------------------------------------------------

    @property
    def is_active(self) -> bool:
        """Indicates if audio capture is active."""
        return self._is_active

    @property
    def is_muted(self) -> bool:
        """Indicates if audio input is currently muted."""
        return self._is_muted

    def enable_microphone(self) -> None:
        """Activates microphone input."""
        self._is_active = True
        logger.info("Microphone input enabled")

    def disable_microphone(self) -> None:
        """Immediate hardware/software kill-switch: wipes buffers and disables recording."""
        self._is_active = False
        self.flush_buffers()
        logger.info("Microphone input DISABLED via privacy kill-switch")

    def mute(self) -> None:
        """Mutes audio ingestion while keeping device initialized."""
        self._is_muted = True
        self.flush_buffers()
        logger.info("Microphone muted")

    def unmute(self) -> None:
        """Unmutes audio ingestion."""
        self._is_muted = False
        logger.info("Microphone unmuted")

    def flush_buffers(self) -> None:
        """Wipes all speech accumulation buffers from memory."""
        self._preroll_buffer.clear()
        self._speech_buffer.clear()
        self._leftover_chunk.clear()
        self.vad.reset()

    def get_status(self) -> MicrophoneStatus:
        """Returns current operational and privacy status."""
        if not self._is_active:
            indicator = "OFF"
        elif self._is_muted:
            indicator = "MUTED"
        elif len(self._speech_buffer) > 0:
            indicator = "RECORDING"
        else:
            indicator = "LISTENING"

        return MicrophoneStatus(
            is_active=self._is_active,
            is_muted=self._is_muted,
            rms_level=self._latest_rms,
            db_level=self._latest_db,
            frames_processed=self._frames_processed,
            privacy_indicator=indicator,
        )

    # --------------------------------------------------------------------------
    # Stream Ingestion & Processing
    # --------------------------------------------------------------------------

    def feed_audio_chunk(self, chunk: bytes) -> Optional[bytes]:
        """Ingests raw PCM audio bytes.

        Returns:
            Complete WAV audio bytes if a complete utterance has finished (SPEECH_ENDED),
            or None if speech is continuing or currently silent.
        """
        # Privacy policy: If disabled or muted, immediately drop all audio data without saving
        if not self._is_active or self._is_muted:
            return None

        if not chunk:
            return None

        # Handle fragmented chunks using leftover buffer
        data = bytes(self._leftover_chunk) + chunk
        self._leftover_chunk.clear()

        complete_utterance: Optional[bytes] = None

        offset = 0
        total_len = len(data)

        while offset + self.frame_bytes <= total_len:
            frame_data = data[offset : offset + self.frame_bytes]
            offset += self.frame_bytes
            self._frames_processed += 1

            frame_metrics = self.vad.compute_frame_metrics(frame_data)
            self._latest_rms = frame_metrics.rms
            self._latest_db = frame_metrics.energy_db

            vad_state = self.vad.process_frame(frame_data)

            if vad_state == VADState.SILENCE:
                self._preroll_buffer.append(frame_data)

            elif vad_state == VADState.SPEECH_STARTED:
                # Prepend preroll buffer frames to capture onset syllables
                for preroll_frame in self._preroll_buffer:
                    self._speech_buffer.extend(preroll_frame)
                self._preroll_buffer.clear()
                self._speech_buffer.extend(frame_data)

            elif vad_state == VADState.SPEECH_ACTIVE:
                self._speech_buffer.extend(frame_data)
                # Safeguard against runaway long recording
                if len(self._speech_buffer) >= self.max_utterance_bytes:
                    complete_utterance = self._package_speech_buffer()

            elif vad_state == VADState.SPEECH_ENDED:
                self._speech_buffer.extend(frame_data)
                complete_utterance = self._package_speech_buffer()

        # Retain remainder bytes for next chunk
        if offset < total_len:
            self._leftover_chunk.extend(data[offset:])

        return complete_utterance

    def _package_speech_buffer(self) -> Optional[bytes]:
        """Converts accumulated speech PCM buffer into standard WAV payload."""
        if not self._speech_buffer or len(self._speech_buffer) < (self.sample_rate * 0.1 * self.sampwidth):
            # Less than 100ms of audio, discard as noise
            self.flush_buffers()
            return None

        wav_bytes = self.create_wav_payload(
            pcm_bytes=bytes(self._speech_buffer),
            sample_rate=self.sample_rate,
            channels=self.channels,
            sampwidth=self.sampwidth,
        )
        self.flush_buffers()
        return wav_bytes

    @staticmethod
    def create_wav_payload(pcm_bytes: bytes, sample_rate: int = 16000, channels: int = 1, sampwidth: int = 2) -> bytes:
        """Wraps raw PCM bytes in a compliant RIFF/WAVE header."""
        out = io.BytesIO()
        with wave.open(out, "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sampwidth)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_bytes)
        return out.getvalue()

