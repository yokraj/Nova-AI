"""Requirement Parser extracts structured info from natural language prompts.
"""

import re
from typing import Dict, List, Any

class RequirementParser:
    """Rule-based requirements parser fallback engine."""

    def parse_text(self, text: str) -> Dict[str, Any]:
        """Parses raw text to extract project, goal, modules, technology, constraints and risks."""
        text_lower = text.lower()
        
        # 1. Determine Project Name
        project_name = "Software System"
        if "ecommerce" in text_lower or "e-commerce" in text_lower:
            project_name = "Ecommerce System"
        elif "blog" in text_lower:
            project_name = "Blog Application"
        elif "chat" in text_lower:
            project_name = "Chat Application"
        elif "todo" in text_lower or "task" in text_lower:
            project_name = "Task Management System"
        else:
            # Try to grab first 3-4 words
            words = text.split()
            if len(words) > 1:
                project_name = f"{' '.join(words[:3])} System"

        # 2. Modules
        modules = []
        if "ecommerce" in text_lower or "e-commerce" in text_lower:
            modules = ["Authentication", "Product Management", "Cart", "Payment", "Orders"]
        elif "blog" in text_lower:
            modules = ["Authentication", "Post Creation", "Comments", "Categories", "Search"]
        elif "chat" in text_lower:
            modules = ["Authentication", "Realtime Messaging", "User Profile", "Channels", "History"]
        else:
            modules = ["Authentication", "Core API", "Database Integration", "User Dashboard"]

        # 3. Technologies
        tech = []
        for word in ["python", "fastapi", "django", "flask", "node.js", "node", "express", "react", "vue", "angular", "go", "rust", "java", "spring boot", "postgresql", "mysql", "mongodb", "redis"]:
            if word in text_lower:
                tech.append(word.title() if word != "node.js" else "Node.js")
        if not tech:
            tech = ["Python", "FastAPI", "PostgreSQL"]

        # 4. Constraints
        constraints = []
        if "offline" in text_lower:
            constraints.append("Must support offline-first execution.")
        if "secure" in text_lower or "security" in text_lower:
            constraints.append("Enforce secure, non-root runtimes.")
        if "zero-cost" in text_lower or "free" in text_lower:
            constraints.append("Zero-cost architecture limitations.")
        if not constraints:
            constraints = ["Must integrate with existing infrastructure.", "Zero-cost local deployment only."]

        # 5. Risks
        risks = []
        if "payment" in text_lower or "stripe" in text_lower:
            risks.append("Third-party payment gateway integration reliability.")
        if "realtime" in text_lower or "chat" in text_lower:
            risks.append("Websocket concurrency scaling limits.")
        if not risks:
            risks = ["Local execution resource limits.", "Offline local model accuracy limits."]

        return {
            "project_name": project_name,
            "goal": f"To build an enterprise {project_name.lower()} meeting the constraints and feature goals.",
            "modules": modules,
            "technology_requirements": tech,
            "constraints": constraints,
            "dependencies": ["Existing Nova Framework runtime"],
            "risks": risks,
        }
