"""Action Planner details structural execution sequences for UI automation.
"""

from typing import List, Optional
from app.ai.vision.models import ActionPlan, ActionStep, UIElement, BoundingBox

class ActionPlanner:
    """Compiles visual element positions and constructs action steps flow plans."""

    def plan_login_sequence(self, elements: List[UIElement]) -> ActionPlan:
        """Generates sequence list targeting field inputs and login trigger."""
        steps = []
        
        # Locate username
        username_el = self._find_element_by_label_or_type(elements, "username", "textbox")
        if username_el:
            steps.append(ActionStep(
                action_type="locate",
                target="Username Field",
                location=username_el.bbox
            ))
            steps.append(ActionStep(
                action_type="type",
                target="Username Field",
                location=username_el.bbox,
                parameters={"text": "admin"}
            ))

        # Locate password
        password_el = self._find_element_by_label_or_type(elements, "password", "textbox")
        if password_el:
            steps.append(ActionStep(
                action_type="locate",
                target="Password Field",
                location=password_el.bbox
            ))
            steps.append(ActionStep(
                action_type="type",
                target="Password Field",
                location=password_el.bbox,
                parameters={"text": "password123"}
            ))

        # Locate login button
        login_el = self._find_element_by_label_or_type(elements, "login", "button")
        if login_el:
            steps.append(ActionStep(
                action_type="locate",
                target="Login Button",
                location=login_el.bbox
            ))
            steps.append(ActionStep(
                action_type="click",
                target="Login Button",
                location=login_el.bbox
            ))
            steps.append(ActionStep(
                action_type="wait",
                target="Page Load",
                parameters={"duration_seconds": 2}
            ))

        return ActionPlan(
            steps=steps,
            confidence=0.95
        )

    def _find_element_by_label_or_type(
        self, elements: List[UIElement], keyword: str, element_type: str
    ) -> Optional[UIElement]:
        """Finds control matching target tag or falls back to element type."""
        for el in elements:
            if el.label and keyword.lower() in el.label.lower():
                return el
        # Fallback to type matching
        for el in elements:
            if el.type.lower() == element_type.lower():
                return el
        return None
