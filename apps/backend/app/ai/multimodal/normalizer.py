"""Multimodal Input Normalizer for Nova-AI Interaction Engine.

Normalizes text, offline Whisper voice audio, and screenshots/images into a canonical
`NormalizedMultimodalInput` with active desktop context and security inspection.
"""

from typing import Any, Dict, Optional
import time
import uuid
import structlog

from app.ai.multimodal.models import (
    ActiveAppContext,
    InputModality,
    NormalizedMultimodalInput,
)
from app.ai.voice.stt_engine import LocalSTTEngine
from app.ai.voice.security_filter import VoiceSecurityFilter, VoiceSecurityError
from app.ai.voice.exceptions import SpeechRecognitionError
from app.ai.desktop_automation.exceptions import ApprovalRequiredError
from app.ai.desktop_automation.window_tracker import WindowTracker
from app.ai.vision.ocr_engine import OCREngine
from app.ai.vision.image_loader import ImageLoader
from app.ai.vision.screenshot_manager import ScreenshotManager

logger = structlog.get_logger("multimodal_normalizer")


class MultimodalInputNormalizer:
    """Normalizes multimodal inputs from diverse sources into a standard representation."""

    def __init__(
        self,
        stt_engine: Optional[LocalSTTEngine] = None,
        window_tracker: Optional[WindowTracker] = None,
        ocr_engine: Optional[OCREngine] = None,
        image_loader: Optional[ImageLoader] = None,
        screenshot_manager: Optional[ScreenshotManager] = None,
    ) -> None:
        self.stt_engine = stt_engine or LocalSTTEngine()
        self.window_tracker = window_tracker or WindowTracker()
        self.ocr_engine = ocr_engine or OCREngine()
        self.image_loader = image_loader or ImageLoader()
        self.screenshot_manager = screenshot_manager or ScreenshotManager()

    async def normalize(
        self,
        text: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        use_screenshot: bool = False,
        session_id: Optional[str] = None,
        active_app_override: Optional[str] = None,
    ) -> NormalizedMultimodalInput:
        """Normalizes heterogeneous input into a single strongly-typed NormalizedMultimodalInput.

        Args:
            text: Optional plain text command.
            audio_bytes: Optional WAV/audio bytes for offline Whisper STT.
            image_path: Optional file path to input image.
            image_bytes: Optional raw image bytes.
            use_screenshot: If True, captures active desktop screenshot.
            session_id: Optional tracking session identifier.
            active_app_override: Optional explicit target application override.

        Returns:
            NormalizedMultimodalInput ready for intent analysis and execution.
        """
        sid = session_id or f"session_{uuid.uuid4().hex[:8]}"
        transcribed_text: Optional[str] = None
        visual_ocr_text: Optional[str] = None

        has_audio = audio_bytes is not None and len(audio_bytes) > 0
        has_text = text is not None and len(text.strip()) > 0
        has_image = (image_path is not None) or (image_bytes is not None) or use_screenshot

        # 1. Determine Input Modality
        if has_audio and (has_image or has_text):
            modality = InputModality.MIXED
        elif has_audio:
            modality = InputModality.VOICE
        elif has_text and has_image:
            modality = InputModality.MIXED
        elif has_image:
            modality = InputModality.SCREENSHOT if use_screenshot else InputModality.IMAGE
        elif has_text:
            modality = InputModality.TEXT
        else:
            raise ValueError("No input provided. At least one of text, audio, image, or screenshot must be specified.")

        # 2. Process Voice Input via Local Whisper STT
        if has_audio:
            try:
                speech_result = await self.stt_engine.transcribe(audio_bytes)
                transcribed_text = speech_result.transcript
                logger.info("Transcribed audio input via local STT", transcript=transcribed_text)
            except Exception as e:
                logger.error("Audio transcription failed", error=str(e))
                raise SpeechRecognitionError(f"Local offline speech recognition failed: {str(e)}") from e

        # 3. Process Vision / Screenshot Input
        if has_image:
            try:
                img = None
                if use_screenshot:
                    img = self.screenshot_manager.capture_screen()
                elif image_bytes or image_path:
                    img = self.image_loader.load(image_path, image_bytes)

                if img is not None:
                    ocr_res = await self.ocr_engine.detect_text(img)
                    text_val = getattr(ocr_res, "full_text", getattr(ocr_res, "text", None))
                    if text_val:
                        visual_ocr_text = text_val.strip()
                        logger.info("Extracted OCR text from visual input", length=len(visual_ocr_text))
            except Exception as e:
                logger.warning("Visual OCR extraction encountered non-critical error", error=str(e))

        # 4. Resolve Active Desktop Context
        active_app_ctx = self._resolve_active_desktop_context(active_app_override)

        # 5. Determine Canonical Effective Text
        if transcribed_text:
            effective_text = transcribed_text.strip()
        elif has_text and text:
            effective_text = text.strip()
        elif visual_ocr_text:
            effective_text = f"Analyze screen content: {visual_ocr_text[:200]}"
        elif has_image:
            effective_text = "Analyze current screen or image"
        else:
            effective_text = ""

        # 6. Apply Security and Prompt Injection Filtering
        approval_flag = False
        if effective_text:
            try:
                VoiceSecurityFilter.inspect_transcript(effective_text)
            except ApprovalRequiredError:
                approval_flag = True

        return NormalizedMultimodalInput(
            input_id=f"in_{uuid.uuid4().hex[:8]}",
            modality=modality,
            raw_text=text,
            transcribed_text=transcribed_text,
            effective_text=effective_text,
            audio_bytes=audio_bytes,
            image_path=image_path,
            image_bytes=image_bytes,
            screenshot_active=use_screenshot,
            active_app=active_app_ctx,
            visual_ocr_text=visual_ocr_text,
            session_id=sid,
            requires_approval=approval_flag,
            timestamp=time.time(),
        )

    def _resolve_active_desktop_context(self, override: Optional[str] = None) -> ActiveAppContext:
        """Queries OS WindowTracker to identify current foreground window and active application."""
        if override:
            return ActiveAppContext(
                app_name=override,
                window_title=f"{override} Window",
                window_handle="0x1000",
                process_id=1234,
                process_name=f"{override.lower()}.exe",
                is_foreground=True,
            )

        try:
            info = self.window_tracker.get_active_window_info()
            title = info.get("title", "")
            proc_name = info.get("executable_name", "")
            handle = str(info.get("handle", "0x0"))
            pid = info.get("process_id", 0)

            # Infer app name from title or process name
            app_name = "System"
            title_lower = title.lower()
            proc_lower = proc_name.lower()

            if "blender" in title_lower or "blender" in proc_lower:
                app_name = "Blender"
            elif "photoshop" in title_lower or "photoshop" in proc_lower:
                app_name = "Photoshop"
            elif "code" in title_lower or "code" in proc_lower:
                app_name = "VS Code"
            elif "chrome" in title_lower or "chrome" in proc_lower:
                app_name = "Google Chrome"
            elif "firefox" in title_lower or "firefox" in proc_lower:
                app_name = "Firefox"
            elif "notepad" in title_lower or "notepad" in proc_lower:
                app_name = "Notepad"
            elif "cmd" in title_lower or "powershell" in title_lower:
                app_name = "Terminal"
            elif title:
                app_name = title.split(" - ")[-1].strip()

            return ActiveAppContext(
                app_name=app_name,
                window_title=title,
                window_handle=handle,
                process_id=pid,
                process_name=proc_name,
                is_foreground=True,
            )
        except Exception as e:
            logger.debug("Active window lookup failed, falling back to System context", error=str(e))
            return ActiveAppContext(
                app_name="System",
                window_title="",
                window_handle="0x0",
                process_id=0,
                process_name="",
                is_foreground=True,
            )
