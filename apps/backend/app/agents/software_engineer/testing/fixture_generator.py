"""Fixture Generator providing reusable mock dictionaries.
"""


class FixtureGenerator:
    """Creates mock configs representing users, roles, services etc."""

    def generate_fixture(self, name: str, fields: dict) -> str:
        """Constructs pytest fixture declarations returning dict scopes.

        Args:
            name: Fixture helper name.
            fields: Initial payload values.

        Returns:
            Source code string.
        """
        import reprlib

        payload = reprlib.repr(fields)
        return (
            "import pytest\n\n"
            f"@pytest.fixture\n"
            f"def {name}_fixture():\n"
            f"    return {payload}\n"
        )
