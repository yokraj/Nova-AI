"""Voice Activity Detection (VAD) Engine for Nova-AI Conversational Assistant.

Provides real-time speech vs silence classification using energy, RMS, and zero-crossing rate
with adaptive background noise floor calibration and hysteresis hangover windowing.
"""

from typing import Dict, List, Optional
import math
import struct
import structlog

from app.ai.voice.conversational.models import AudioFrame, VADState

logger = structlog.get_logger("conversational_vad")


class VoiceActivityDetector:
    """Classifies streaming PCM audio into VADState (SILENCE, SPEECH_STARTED, SPEECH_ACTIVE, SPEECH_ENDED)."""

    def __init__(
        self,
        sample_rate: int = 16000,
        frame_duration_ms: int = 20,
        speech_start_threshold_db: float = -42.0,
        speech_end_threshold_db: float = -48.0,
        min_speech_frames: int = 3,  # ~60ms to trigger speech start
        hangover_frames: int = 15,    # ~300ms pause allowed before declaring speech ended
    ) -> None:
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.bytes_per_sample = 2  # 16-bit mono PCM
        self.frame_size = int((sample_rate * frame_duration_ms) / 1000) * self.bytes_per_sample

        self.speech_start_threshold_db = speech_start_threshold_db
        self.speech_end_threshold_db = speech_end_threshold_db
        self.min_speech_frames = min_speech_frames
        self.hangover_frames = hangover_frames

        # State tracking
        self.current_state = VADState.SILENCE
        self.consecutive_speech_frames = 0
        self.consecutive_silence_frames = 0
        self.noise_floor_db = -65.0
        self.total_frames_processed = 0

    def compute_frame_metrics(self, frame_bytes: bytes) -> AudioFrame:
        """Computes RMS, energy in dBFS, and zero-crossing rate for raw 16-bit PCM mono bytes."""
        if not frame_bytes or len(frame_bytes) < 2:
            return AudioFrame(data=frame_bytes, rms=0.0, energy_db=-100.0, is_speech=False)

        num_samples = len(frame_bytes) // 2
        try:
            samples = struct.unpack(f"<{num_samples}h", frame_bytes[: num_samples * 2])
        except struct.error:
            return AudioFrame(data=frame_bytes, rms=0.0, energy_db=-100.0, is_speech=False)

        if not samples:
            return AudioFrame(data=frame_bytes, rms=0.0, energy_db=-100.0, is_speech=False)

        sum_sq = sum(s * s for s in samples)
        rms = math.sqrt(sum_sq / num_samples)

        # Calculate dBFS relative to max 16-bit value (32768)
        energy_db = 20.0 * math.log10(rms / 32768.0 + 1e-9)

        # Zero-crossing rate
        zcr = 0.0
        if num_samples > 1:
            crossings = sum(1 for i in range(1, num_samples) if (samples[i] >= 0) != (samples[i - 1] >= 0))
            zcr = crossings / (num_samples - 1)

        is_active = energy_db > self.speech_start_threshold_db

        return AudioFrame(
            data=frame_bytes,
            rms=rms,
            energy_db=energy_db,
            is_speech=is_active,
            zero_crossing_rate=zcr,
        )

    def process_frame(self, frame_bytes: bytes) -> VADState:
        """Processes a single audio frame and updates the VAD state machine."""
        frame = self.compute_frame_metrics(frame_bytes)
        self.total_frames_processed += 1

        # Adaptive background noise tracking
        if frame.energy_db < self.speech_end_threshold_db:
            # Slow adaptation to ambient floor
            self.noise_floor_db = 0.95 * self.noise_floor_db + 0.05 * frame.energy_db

        if self.current_state in [VADState.SILENCE, VADState.SPEECH_ENDED]:
            if frame.energy_db >= self.speech_start_threshold_db:
                self.consecutive_speech_frames += 1
                if self.consecutive_speech_frames >= self.min_speech_frames:
                    self.current_state = VADState.SPEECH_STARTED
                    self.consecutive_silence_frames = 0
                else:
                    self.current_state = VADState.SILENCE
            else:
                self.consecutive_speech_frames = 0
                self.current_state = VADState.SILENCE

        elif self.current_state in [VADState.SPEECH_STARTED, VADState.SPEECH_ACTIVE]:
            if frame.energy_db >= self.speech_end_threshold_db:
                self.consecutive_silence_frames = 0
                self.current_state = VADState.SPEECH_ACTIVE
            else:
                self.consecutive_silence_frames += 1
                if self.consecutive_silence_frames >= self.hangover_frames:
                    self.current_state = VADState.SPEECH_ENDED
                    self.consecutive_speech_frames = 0
                else:
                    # Within hangover window: still active speech
                    self.current_state = VADState.SPEECH_ACTIVE

        return self.current_state

    def calibrate_noise_floor(self, ambient_audio_chunks: List[bytes]) -> float:
        """Calibrates initial background ambient noise floor from silence samples."""
        if not ambient_audio_chunks:
            return self.noise_floor_db

        db_values = [self.compute_frame_metrics(chunk).energy_db for chunk in ambient_audio_chunks if chunk]
        if db_values:
            self.noise_floor_db = sum(db_values) / len(db_values)
            # Dynamically bias thresholds based on measured noise
            self.speech_start_threshold_db = max(-48.0, self.noise_floor_db + 15.0)
            self.speech_end_threshold_db = max(-54.0, self.noise_floor_db + 8.0)
            logger.info(
                "Calibrated VAD noise floor",
                noise_floor_db=round(self.noise_floor_db, 2),
                speech_start_db=round(self.speech_start_threshold_db, 2),
            )
        return self.noise_floor_db

    def reset(self) -> None:
        """Resets state machine counters."""
        self.current_state = VADState.SILENCE
        self.consecutive_speech_frames = 0
        self.consecutive_silence_frames = 0

    def get_metrics(self) -> Dict[str, float]:
        """Returns current operational telemetry."""
        return {
            "noise_floor_db": self.noise_floor_db,
            "speech_start_threshold_db": self.speech_start_threshold_db,
            "speech_end_threshold_db": self.speech_end_threshold_db,
            "frames_processed": float(self.total_frames_processed),
        }

