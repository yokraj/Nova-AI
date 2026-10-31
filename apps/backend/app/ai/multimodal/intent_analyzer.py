"""Multimodal Intent Analyzer for Nova-AI Interaction Engine.

Extracts intent, goals, entities, constraints, and screen references from multimodal inputs,
resolves multi-turn follow-ups, and detects ambiguity requiring clarification.
"""

from typing import Any, Dict, List, Optional, Tuple
import re
import structlog
import uuid

from app.ai.multimodal.models import (
    ClarificationOption,
    ClarificationRequest,
    IntentCategory,
    MultimodalConversationContext,
    NormalizedMultimodalInput,
    ScreenReference,
    StructuredTaskRequest,
)
from app.ai.multimodal.vision_grounding import MultimodalVisionGrounder
from app.ai.kernel.model_router import CognitiveWorkloadType, LocalModelRouter
from app.ai.kernel.kernel_security import KernelSecurityGuard

logger = structlog.get_logger("multimodal_intent_analyzer")


class MultimodalIntentAnalyzer:
    """Performs deep semantic understanding, entity extraction, and ambiguity resolution."""

    def __init__(
        self,
        vision_grounder: Optional[MultimodalVisionGrounder] = None,
        model_router: Optional[LocalModelRouter] = None,
        security_guard: Optional[KernelSecurityGuard] = None,
    ) -> None:
        self.vision_grounder = vision_grounder or MultimodalVisionGrounder()
        self.model_router = model_router or LocalModelRouter.get_instance()
        self.security_guard = security_guard or KernelSecurityGuard()

    async def analyze_intent(
        self,
        normalized_input: NormalizedMultimodalInput,
        context: MultimodalConversationContext,
    ) -> StructuredTaskRequest:
        """Analyzes normalized multimodal input to produce a StructuredTaskRequest.

        Args:
            normalized_input: Standardized input containing text, audio, image, and active app context.
            context: Active conversation context for resolving follow-ups.

        Returns:
            StructuredTaskRequest with all extracted parameters, permissions, and clarification flags.
        """
        text = normalized_input.effective_text.strip()
        lower_text = text.lower()

        # 1. Check for cancellation / abort commands
        if self._is_cancel_command(lower_text):
            return StructuredTaskRequest(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                intent_category=IntentCategory.CANCEL_ACTION,
                primary_goal="Cancel current action or task",
                action_type="cancel",
                confidence=1.0,
            )

        # 2. Check for Clarification Answers
        if context.pending_clarification:
            resolved_req = self._resolve_clarification_response(
                text, context.pending_clarification, context
            )
            if resolved_req:
                return resolved_req

        # 3. Handle Screen References & Visual Grounding
        screen_refs: List[ScreenReference] = []
        visual_uncertainty = False
        uncertainty_reason: Optional[str] = None

        visual_trigger_phrases = ["click", "press", "button", "icon", "on the screen", "this window", "menu", "select"]
        if any(vp in lower_text for vp in visual_trigger_phrases):
            target_label = self._extract_visual_target_phrase(lower_text)
            if target_label:
                ref = await self.vision_grounder.ground_reference(
                    reference_text=target_label,
                    image_path=normalized_input.image_path,
                    image_bytes=normalized_input.image_bytes,
                    screenshot_active=normalized_input.screenshot_active,
                )
                screen_refs.append(ref)
                if ref.is_uncertain:
                    visual_uncertainty = True
                    uncertainty_reason = f"Visual reference '{target_label}' is ambiguous or below confidence threshold ({ref.confidence:.2f})."

        # 4. Resolve Target Application (prioritize explicit mention, then active app, then context history)
        target_app = self._resolve_target_app(lower_text, normalized_input, context)

        # 5. Extract Intent Category & Goal Decomposition
        intent_cat, action_type, params, entities, constraints = self._extract_intent_details(
            text, lower_text, target_app, context
        )

        # 6. Check for Missing Essential Information requiring clarification
        needs_clarification = False
        clarification_req: Optional[ClarificationRequest] = None

        if visual_uncertainty:
            needs_clarification = True
            clarification_req = ClarificationRequest(
                prompt=f"I found multiple or unclear screen elements matching your request. Could you clarify which one to click?",
                question="Please clarify the target screen element.",
                options=[
                    ClarificationOption(option_id="opt_1", label="First visible matching element", description="Select the top-left element"),
                    ClarificationOption(option_id="opt_2", label="Specify exact button name", description="Type or say the exact button label"),
                ],
                missing_parameter="target_element",
                reason=uncertainty_reason or "Visual uncertainty",
            )
        elif self._is_missing_essential_parameter(action_type, params, lower_text):
            needs_clarification = True
            clarification_req = self._build_clarification_request(action_type, text, target_app)

        # 7. Check Security Policy & Approval
        requires_approval = normalized_input.requires_approval or self.security_guard.check_approval_required(
            action_type=action_type,
            parameters={**params, "raw_query": text, "target_app": target_app},
        )

        return StructuredTaskRequest(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            intent_category=intent_cat,
            primary_goal=text,
            target_app=target_app,
            action_type=action_type,
            parameters=params,
            entities=entities,
            constraints=constraints,
            screen_references=screen_refs,
            required_permissions=["desktop_automation", "system_execute"] if action_type != "conversation" else [],
            requires_user_approval=requires_approval,
            needs_clarification=needs_clarification,
            clarification_request=clarification_req,
            confidence=0.95 if not visual_uncertainty else 0.50,
            visual_uncertainty=visual_uncertainty,
            uncertainty_reason=uncertainty_reason,
        )

    def _is_cancel_command(self, lower_text: str) -> bool:
        """Checks if the user command is an interruption or cancel instruction."""
        cancel_phrases = ["cancel", "stop", "abort", "halt", "nevermind", "never mind", "shut up", "quit"]
        tokens = re.findall(r"\b\w+\b", lower_text)
        return any(cp in lower_text for cp in cancel_phrases) and len(tokens) <= 4

    def _resolve_clarification_response(
        self,
        text: str,
        pending_clarification: ClarificationRequest,
        context: MultimodalConversationContext,
    ) -> Optional[StructuredTaskRequest]:
        """Resolves user answer against pending clarification options."""
        lower_text = text.lower().strip()

        # Check for numeric or option ID selection
        matched_option: Optional[ClarificationOption] = None
        for i, opt in enumerate(pending_clarification.options, 1):
            if opt.option_id.lower() in lower_text or str(i) == lower_text or opt.label.lower() in lower_text:
                matched_option = opt
                break

        # Check for simple affirmative ("yes", "confirm", "proceed")
        if not matched_option and any(aff in lower_text for aff in ["yes", "proceed", "confirm", "do it", "sure"]):
            if pending_clarification.options:
                matched_option = pending_clarification.options[0]

        if matched_option:
            last_req = context.last_task_request
            base_app = last_req.target_app if last_req else "System"
            base_action = matched_option.target_intent or (last_req.action_type if last_req else "clarification_resolved")

            params = dict(last_req.parameters) if last_req else {}
            params.update(matched_option.resolved_parameters)
            params["clarified_selection"] = matched_option.label

            return StructuredTaskRequest(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                intent_category=IntentCategory.CLARIFICATION_ANSWER,
                primary_goal=f"Execute clarified action: {matched_option.label}",
                target_app=base_app,
                action_type=base_action,
                parameters=params,
                confidence=1.0,
            )

        return None

    def _resolve_target_app(
        self,
        lower_text: str,
        normalized_input: NormalizedMultimodalInput,
        context: MultimodalConversationContext,
    ) -> str:
        """Determines target application from text, active window, or previous context."""
        # 1. Explicit app mentions in text
        if "blender" in lower_text:
            return "Blender"
        if "photoshop" in lower_text:
            return "Photoshop"
        if "vscode" in lower_text or "vs code" in lower_text:
            return "VS Code"
        if "browser" in lower_text or "chrome" in lower_text:
            return "Google Chrome"
        if "terminal" in lower_text or "cmd" in lower_text or "powershell" in lower_text:
            return "Terminal"

        # 2. Deictic references ("in it", "in this app", "here")
        if any(deictic in lower_text for deictic in ["in it", "in this", "in that", "here", "active window"]):
            if context.active_app:
                return context.active_app
            if normalized_input.active_app and normalized_input.active_app.app_name != "System":
                return normalized_input.active_app.app_name

        # 3. Active foreground window
        if normalized_input.active_app and normalized_input.active_app.app_name != "System":
            return normalized_input.active_app.app_name

        # 4. Context fallback
        if context.active_app:
            return context.active_app

        return "System"

    def _extract_visual_target_phrase(self, lower_text: str) -> Optional[str]:
        """Extracts the specific visual target element phrase from the command."""
        match = re.search(r"(?:click|press|tap)\s+(?:on\s+)?(?:the\s+)?([a-zA-Z0-9_\-\s]+?)(?:\s+button|\s+icon|\s+in|$)", lower_text)
        if match:
            return match.group(1).strip()

        if "save" in lower_text:
            return "Save"
        if "cancel" in lower_text:
            return "Cancel"
        if "run" in lower_text:
            return "Run"
        if "submit" in lower_text:
            return "Submit"

        return None

    def _extract_intent_details(
        self,
        raw_text: str,
        lower_text: str,
        target_app: str,
        context: MultimodalConversationContext,
    ) -> Tuple[IntentCategory, str, Dict[str, Any], Dict[str, Any], List[str]]:
        """Deconstructs user prompt into intent category, action type, parameters, entities, and constraints."""
        params: Dict[str, Any] = {}
        entities: Dict[str, Any] = {}
        constraints: List[str] = []

        # Application specific rules
        if target_app == "Blender":
            if "cube" in lower_text or "create cube" in lower_text:
                return (
                    IntentCategory.APPLICATION_CONTROL,
                    "create_object",
                    {"primitive": "cube", "target_label": "VoiceCube"},
                    {"object_name": "VoiceCube", "primitive": "cube"},
                    constraints,
                )
            elif "sphere" in lower_text:
                return (
                    IntentCategory.APPLICATION_CONTROL,
                    "create_object",
                    {"primitive": "uv_sphere", "target_label": "VoiceSphere"},
                    {"object_name": "VoiceSphere", "primitive": "uv_sphere"},
                    constraints,
                )
            elif "delete" in lower_text:
                # Check target object
                target_obj = "VoiceCube" if "cube" in lower_text else ("VoiceSphere" if "sphere" in lower_text else None)
                if target_obj:
                    return (
                        IntentCategory.APPLICATION_CONTROL,
                        "delete_object",
                        {"target_label": target_obj},
                        {"target_object": target_obj},
                        constraints,
                    )
                else:
                    return (
                        IntentCategory.APPLICATION_CONTROL,
                        "delete_object",
                        {},  # Missing target parameter!
                        {},
                        constraints,
                    )

        # Desktop GUI actions
        if "click" in lower_text or "press" in lower_text:
            target_label = self._extract_visual_target_phrase(lower_text) or "button"
            return (
                IntentCategory.DESKTOP_ACTION,
                "gui_click",
                {"target_label": target_label},
                {"target_control": target_label},
                constraints,
            )

        if "open" in lower_text or "launch" in lower_text:
            match = re.search(r"(?:open|launch)\s+([a-zA-Z0-9_\-]+)", lower_text)
            app_to_open = match.group(1).title() if match else target_app
            return (
                IntentCategory.DESKTOP_ACTION,
                "launch_application",
                {"application_name": app_to_open},
                {"target_app": app_to_open},
                constraints,
            )

        if "delete" in lower_text or "remove" in lower_text:
            return (
                IntentCategory.DESKTOP_ACTION,
                "delete_file",
                {},  # Missing parameter
                {},
                constraints,
            )

        if "research" in lower_text or "search" in lower_text or "find papers" in lower_text:
            return (
                IntentCategory.RESEARCH_QUERY,
                "research_topic",
                {"query": raw_text},
                {"topic": raw_text},
                constraints,
            )

        # General conversation
        return (
            IntentCategory.CONVERSATION,
            "conversation",
            {"message": raw_text},
            {},
            constraints,
        )

    def _is_missing_essential_parameter(self, action_type: str, params: Dict[str, Any], lower_text: str) -> bool:
        """Determines if the action lacks essential parameters to execute safely."""
        if action_type in ["delete_object", "delete_file"]:
            return "target_label" not in params and "filename" not in params
        if action_type == "gui_click":
            return not params.get("target_label")
        return False

    def _build_clarification_request(self, action_type: str, raw_text: str, target_app: str) -> ClarificationRequest:
        """Generates smart clarification options for missing parameters."""
        if action_type in ["delete_object", "delete_file"]:
            return ClarificationRequest(
                prompt=f"Which target would you like to delete in {target_app}?",
                question="Please specify what to delete.",
                options=[
                    ClarificationOption(
                        option_id="opt_cube",
                        label="Delete VoiceCube",
                        description="Delete the most recently created cube",
                        target_intent="delete_object",
                        resolved_parameters={"target_label": "VoiceCube"},
                    ),
                    ClarificationOption(
                        option_id="opt_all",
                        label="Delete Selected Objects",
                        description="Delete currently selected elements in viewport",
                        target_intent="delete_object",
                        resolved_parameters={"target_label": "selected"},
                    ),
                ],
                missing_parameter="target_label",
                reason="Target object not specified in delete command",
            )

        return ClarificationRequest(
            prompt="Could you clarify what you would like to do?",
            question="Clarification required.",
            options=[],
            missing_parameter="action_target",
            reason="Ambiguous request parameters",
        )
