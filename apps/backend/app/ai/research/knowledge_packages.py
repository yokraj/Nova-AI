"""Knowledge Package Manager handling reusable structured knowledge packages.
"""

from typing import Dict, List, Optional
from app.ai.research.models import KnowledgePackage


class KnowledgePackageManager:
    """Manages reusable Knowledge Packages (documentation, examples, best practices, common errors)."""

    def __init__(self) -> None:
        self._packages: Dict[str, KnowledgePackage] = self._seed_packages()

    def _seed_packages(self) -> Dict[str, KnowledgePackage]:
        pkg = KnowledgePackage(
            topic="React",
            documentation="React user interface library documentation and hooks reference.",
            examples=["const [state, setState] = useState(initial);", "useEffect(() => { ... }, []);"],
            best_practices=["Keep components small and focused", "Use standard custom hooks for shared state logic"],
            common_errors=["Mutating state directly", "Missing dependency array in useEffect"],
            api_reference={"useState": "State hook", "useEffect": "Side-effect hook", "useContext": "Context hook"},
        )
        return {pkg.topic.lower(): pkg}

    def get_package(self, topic: str) -> Optional[KnowledgePackage]:
        """Retrieves stored Knowledge Package by topic string."""
        return self._packages.get(topic.lower())

    def save_package(self, package: KnowledgePackage) -> None:
        """Stores Knowledge Package for future reasoning reuse."""
        self._packages[package.topic.lower()] = package

    def list_packages(self) -> List[KnowledgePackage]:
        """Lists all stored Knowledge Packages."""
        return list(self._packages.values())
