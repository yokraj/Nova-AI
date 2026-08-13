"""Generates API and routing controllers tests.
"""


class APITestGenerator:
    """Produces routing client mock tests templates."""

    def generate_api_test(self, route_path: str, methods: list[str]) -> str:
        """Constructs TestClient requests checking status validations.

        Args:
            route_path: FastAPI route path.
            methods: HTTP methods supported (GET, POST).

        Returns:
            Source code string.
        """
        code_lines = [
            "import pytest",
            "from fastapi.testclient import TestClient",
            "",
        ]
        for m in methods:
            m_lower = m.lower()
            code_lines.append(
                f"def test_{m_lower}_endpoint(client: TestClient):\n"
                f"    response = client.{m_lower}('{route_path}')\n"
                f"    assert response.status_code in (200, 201)\n"
            )

        return "\n".join(code_lines)
