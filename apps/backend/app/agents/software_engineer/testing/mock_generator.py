"""Mock Generator supporting stub classes configurations.
"""


class MockGenerator:
    """Creates database repositories or gateway stubs."""

    def generate_repository_mock(self, repository_class_name: str) -> str:
        """Constructs mock class declarations inheriting base operations.

        Args:
            repository_class_name: Name of original repository.

        Returns:
            Mock class string representation.
        """
        return (
            f"class Mock{repository_class_name}:\n"
            "    def __init__(self):\n"
            "        self.store = {}\n"
            "    def get_by_id(self, entity_id):\n"
            "        return self.store.get(entity_id)\n"
        )
