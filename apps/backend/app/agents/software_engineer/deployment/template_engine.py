"""Lightweight Template Engine for generating deployment files.
"""

from typing import Any, Dict

class TemplateEngine:
    """Renders text templates by substituting double curly-brace placeholders."""

    @staticmethod
    def render(template_str: str, context: Dict[str, Any]) -> str:
        """Replaces {{key}} with value from the context dictionary.
        
        Supports basic conditional lines starting with:
        #if key
        #endif
        """
        lines = template_str.splitlines()
        rendered_lines = []
        skip = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#if "):
                key = stripped[4:].strip()
                # Check if key is true/exists in context
                val = context.get(key)
                if not val:
                    skip = True
                continue
            elif stripped == "#endif":
                skip = False
                continue
                
            if skip:
                continue
                
            # Perform substitutions
            for k, v in context.items():
                placeholder = "{{" + str(k) + "}}"
                if placeholder in line:
                    line = line.replace(placeholder, str(v))
            rendered_lines.append(line)
            
        return "\n".join(rendered_lines)
