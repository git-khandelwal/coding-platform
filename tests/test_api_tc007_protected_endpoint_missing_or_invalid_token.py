import pytest
import requests

BASE_URL = "http://localhost:5000"
PROTECTED_ENDPOINT = f"{BASE_URL}/protected"

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    # Setup: Ensure test user exists (register if not), no teardown needed for this test
    register_url = f"{BASE_URL}/register"
    payload = {"username": "test", "password": "1234"}
    # Try to register; ignore error if user already exists
    try:
        requests.post(register_url, json=payload, timeout=5)
    except Exception:
        pass
    yield
    # No teardown required for this test

def test_protected_endpoint_missing_or_invalid_token():
    # Step 1: Access protected endpoint with NO token
    response_no_token = requests.get(PROTECTED_ENDPOINT)
    assert response_no_token.status_code == 401, (
        f"Expected 401 Unauthorized when no token is provided, got {response_no_token.status_code}"
    )

    # Step 2: Access protected endpoint with INVALID token
    headers = {"Authorization": "Bearer invalidtoken123"}
    response_invalid_token = requests.get(PROTECTED_ENDPOINT, headers=headers)
    assert response_invalid_token.status_code == 401, (
        f"Expected 401 Unauthorized when invalid token is provided, got {response_invalid_token.status_code}"
    )