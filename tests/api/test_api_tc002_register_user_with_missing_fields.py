import pytest
import requests

@pytest.fixture(scope="module")
def base_url():
    # NOTE: The base URL for the API must be provided/configured.
    # If unknown, replace with the correct URL, e.g., "http://localhost:5000"
    return "http://localhost:5000"

@pytest.fixture(scope="function", autouse=True)
def cleanup_users():
    # NOTE: No teardown logic implemented.
    # If a cleanup is required (e.g., removing test users), implement here.
    yield
    # Cleanup logic (if needed) goes here.

@pytest.mark.parametrize(
    "payload,missing_field",
    [
        ({"password": "testpassword"}, "username"),
        ({"username": "testuser"}, "password"),
        ({}, "both"),
    ]
)
def test_register_user_with_missing_fields_TC002(base_url, payload, missing_field):
    url = f"{base_url}/register"
    response = requests.post(url, json=payload)
    assert response.status_code == 400, f"Expected 400 Bad Request when missing {missing_field}, got {response.status_code}"
    try:
        body = response.json()
    except Exception:
        pytest.fail("Response is not valid JSON")
    assert "error" in body, "Response JSON should contain 'error' key"
    assert body["error"] == "Username and password are required", f"Expected error message for missing {missing_field}, got: {body['error']}"