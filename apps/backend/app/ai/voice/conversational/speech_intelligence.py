"""Speech Intelligence Engine for Nova-AI Conversational Voice Assistant (Phase 10M-B).

Detects incomplete commands, resolves conversational self-corrections ("no wait", "actually"),
distinguishes chitchat from actionable goals, and supports multilingual speech processing.
"""

from typing import Any, Dict, List, Optional, Tuple
import re
import structlog

from app.ai.voice.conversational.models import SpeechAnalysisResult, SpeechIntentType

logger = structlog.get_logger("conversational_speech_intelligence")


class SpeechIntelligenceEngine:
    """Extracts structured intent, resolves verbal repairs, and handles incomplete commands."""

    # Verbal repair and self-correction patterns
    REPAIR_PATTERNS = [
        r"(.*?)\s+(?:no\s+wait|no\s+scratch\s+that|scratch\s+that)[\s,]+(.*)",
        r"(.*?)\s+(?:actually|wait\s+actually)[\s,]+(?:make\s+it|make\s+that)?\s*(.*)",
        r"(.*?)\s+(?:i\s+mean|i\s+meant)[\s,]+(.*)",
        r"(.*?)\s+(?:cancel\s+that[\s,]+(?:open|create|do|run)?\s*)(.*)",
        r"(.*?)\s+(?:sorry[\s,]+(?:i\s+meant\s+)?)(.*)",
        r"(.*?)\s+(?:wait[\s,]+)(.*)",
    ]

    # Incomplete command trailing patterns
    INCOMPLETE_PATTERNS = [
        (r"^(?:open|launch|start)(?:\s+(?:the|a|an))?\s*$", "application_name", "Which application would you like me to open?"),
        (r"^(?:create|make|add)(?:\s+(?:a|an|the))?\s*$", "object_type", "What object would you like me to create?"),
        (r"^(?:delete|remove|clear)(?:\s+(?:the|a|this|that))?\s*$", "target_item", "Which item should I delete?"),
        (r"^(?:save|export)(?:\s+(?:to|as))?\s*$", "destination_path", "Where would you like me to save the file?"),
        (r"^(?:click|press)(?:\s+(?:the|on))?\s*$", "ui_element", "Which button or element should I click?"),
        (r"^(?:search|find)(?:\s+for)?\s*$", "search_query", "What would you like me to search for?"),
        (r"\b(?:in|at|to|for|with|and|or|of|from)\s*$", "target_context", "Could you specify what should follow that?"),
    ]

    # System controls
    SYSTEM_CONTROLS = {
        "stop": "STOP",
        "cancel": "CANCEL",
        "halt": "STOP",
        "pause": "PAUSE",
        "resume": "RESUME",
        "continue": "RESUME",
        "mute": "MUTE",
        "unmute": "UNMUTE",
        "shut up": "MUTE",
        "quiet": "MUTE",
        "be quiet": "MUTE",
        "never mind": "CANCEL",
        "abort": "CANCEL",
    }

    # Chitchat responses
    CHITCHAT_RESPONSES = {
        "hello": "Hello! How can I help you today?",
        "hi": "Hi there! What can I do for you?",
        "hey": "Hey! Ready for your command.",
        "good morning": "Good morning! How can I assist you?",
        "good afternoon": "Good afternoon! What are we working on?",
        "good evening": "Good evening! How can I help?",
        "how are you": "I'm running smoothly and fully local. What would you like to do?",
        "who are you": "I am Nova, your local conversational AI desktop assistant.",
        "what can you do": "I can automate desktop apps, manipulate 3D scenes, manage files, and browse the web.",
        "thank you": "You're very welcome!",
        "thanks": "Glad to help!",
        "bye": "Goodbye! Let me know whenever you need me.",
        "goodbye": "Goodbye! Have a great day.",
    }

    def __init__(self, default_language: str = "en") -> None:
        self.default_language = default_language

    def analyze_speech(
        self,
        transcript: str,
        language: str = "en",
        has_active_task: bool = False,
    ) -> SpeechAnalysisResult:
        """Deconstructs speech transcript into intent, structured goals, and repair corrections.

        Args:
            transcript: Transcribed speech text.
            language: ISO language code (e.g. 'en', 'es', 'fr', 'de').
            has_active_task: Whether a task is currently executing.

        Returns:
            SpeechAnalysisResult with intent classification and extracted parameters.
        """
        raw_text = transcript.strip()
        lower_text = raw_text.lower().rstrip(".,!?")

        if not raw_text:
            return SpeechAnalysisResult(
                raw_transcript="",
                cleaned_transcript="",
                intent_type=SpeechIntentType.INCOMPLETE,
                target_goal="",
                is_incomplete=True,
                missing_information_prompt="I didn't catch that. Could you repeat?",
                detected_language=language,
                confidence=0.0,
            )

        # 1. System Control Fast-Path (Stop, Cancel, Mute)
        for ctrl_phrase, ctrl_action in self.SYSTEM_CONTROLS.items():
            if lower_text == ctrl_phrase or lower_text.startswith(f"{ctrl_phrase} "):
                return SpeechAnalysisResult(
                    raw_transcript=raw_text,
                    cleaned_transcript=lower_text,
                    intent_type=SpeechIntentType.SYSTEM_CONTROL,
                    target_goal=ctrl_action,
                    parameters={"action": ctrl_action},
                    detected_language=language,
                    confidence=1.0,
                )

        # 2. Verbal Self-Correction / Speech Repair Detection
        corrected_from: Optional[str] = None
        effective_text = raw_text

        for pat in self.REPAIR_PATTERNS:
            match = re.search(pat, raw_text, flags=re.IGNORECASE)
            if match:
                initial_part = match.group(1).strip()
                repair_part = match.group(2).strip()

                if repair_part:
                    corrected_from = initial_part
                    effective_text = repair_part
                    logger.info("Detected spoken self-correction", initial=initial_part, corrected=repair_part)
                    break

        clean_lower = effective_text.lower().rstrip(".,!?")

        # 3. Chitchat Detection
        for chitchat_phrase, chitchat_reply in self.CHITCHAT_RESPONSES.items():
            if clean_lower == chitchat_phrase or clean_lower.startswith(f"{chitchat_phrase} nova"):
                return SpeechAnalysisResult(
                    raw_transcript=raw_text,
                    cleaned_transcript=effective_text,
                    intent_type=SpeechIntentType.CHITCHAT_CONVERSATION,
                    target_goal="chitchat",
                    parameters={"response": chitchat_reply},
                    corrected_from=corrected_from,
                    detected_language=language,
                    confidence=0.98,
                )

        # 4. Incomplete Command Detection
        for pat, slot, prompt_msg in self.INCOMPLETE_PATTERNS:
            if re.search(pat, clean_lower):
                return SpeechAnalysisResult(
                    raw_transcript=raw_text,
                    cleaned_transcript=effective_text,
                    intent_type=SpeechIntentType.INCOMPLETE,
                    target_goal=effective_text,
                    is_incomplete=True,
                    missing_information_prompt=prompt_msg,
                    parameters={"missing_slot": slot},
                    corrected_from=corrected_from,
                    detected_language=language,
                    confidence=0.90,
                )

        # 5. Actionable Command Decomposition
        target_app, action_type, params = self._extract_action_parameters(clean_lower)

        intent_type = SpeechIntentType.CORRECTION if corrected_from else SpeechIntentType.ACTIONABLE_COMMAND

        return SpeechAnalysisResult(
            raw_transcript=raw_text,
            cleaned_transcript=effective_text,
            intent_type=intent_type,
            target_goal=effective_text,
            target_app=target_app,
            parameters=params,
            is_incomplete=False,
            corrected_from=corrected_from,
            detected_language=language,
            confidence=0.95,
        )

    def _extract_action_parameters(self, text: str) -> Tuple[str, str, Dict[str, Any]]:
        """Extracts target application, action type, and parameters from spoken instruction."""
        target_app = "System"
        action_type = "execute"
        params: Dict[str, Any] = {}

        if "blender" in text:
            target_app = "Blender"
        elif "photoshop" in text:
            target_app = "Photoshop"
        elif "chrome" in text or "browser" in text:
            target_app = "Google Chrome"
        elif "code" in text or "vscode" in text:
            target_app = "VS Code"
        elif "notepad" in text:
            target_app = "Notepad"

        # Action mapping
        if "cube" in text:
            action_type = "create_object"
            params = {"primitive": "cube", "target_label": "VoiceCube"}
            target_app = "Blender"
        elif "sphere" in text:
            action_type = "create_object"
            params = {"primitive": "uv_sphere", "target_label": "VoiceSphere"}
            target_app = "Blender"
        elif "cylinder" in text:
            action_type = "create_object"
            params = {"primitive": "cylinder", "target_label": "VoiceCylinder"}
            target_app = "Blender"
        elif "delete" in text:
            action_type = "delete_object"
            params = {"target_label": "SelectedObject"}
        elif "save" in text:
            action_type = "save_file"
            params = {"filename": "voice_scene.blend"}
        elif "click" in text:
            action_type = "gui_click"
            # Extract target label after 'click'
            match = re.search(r"click\s+(?:the\s+)?(.*?)(?:\s+button)?$", text)
            label = match.group(1).strip() if match else text
            params = {"target_label": label}
        elif "open" in text or "launch" in text:
            action_type = "launch_application"
            params = {"app_name": target_app}

        return target_app, action_type, params

