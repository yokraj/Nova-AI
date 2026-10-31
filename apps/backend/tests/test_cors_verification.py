import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from starlette.testclient import TestClient
from app.main import app

def test_cors():
    client = TestClient(app)
    origins_to_test = [
        ("http://127.0.0.1:3000", True),
        ("http://localhost:3000", True),
        ("http://127.0.0.1:5173", True),
        ("http://localhost:5173", True),
        ("http://unauthorized-domain.com", False),
    ]

    for origin, should_allow in origins_to_test:
        preflight = client.options(
            "/api/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )
        get_res = client.get("/api/health", headers={"Origin": origin})
        print(f"Origin: {origin}")
        print(f"  Preflight status: {preflight.status_code}")
        print(f"  Preflight Allow-Origin: {preflight.headers.get('access-control-allow-origin')}")
        print(f"  Preflight Allow-Credentials: {preflight.headers.get('access-control-allow-credentials')}")
        print(f"  GET status: {get_res.status_code}")
        print(f"  GET Allow-Origin: {get_res.headers.get('access-control-allow-origin')}")
        print(f"  GET Allow-Credentials: {get_res.headers.get('access-control-allow-credentials')}")

        if should_allow:
            assert preflight.status_code == 200, f"Expected 200 preflight for {origin}, got {preflight.status_code}"
            assert preflight.headers.get("access-control-allow-origin") == origin, f"Preflight Origin header mismatch for {origin}"
            assert preflight.headers.get("access-control-allow-credentials") == "true", f"Missing credentials header for {origin}"
            assert get_res.headers.get("access-control-allow-origin") == origin, f"GET Origin header mismatch for {origin}"
            assert get_res.headers.get("access-control-allow-credentials") == "true", f"Missing credentials header for {origin}"
        else:
            assert preflight.headers.get("access-control-allow-origin") is None, f"Expected None for unauthorized origin, got {preflight.headers.get('access-control-allow-origin')}"

    print("\nALL CORS ASSERTIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_cors()

