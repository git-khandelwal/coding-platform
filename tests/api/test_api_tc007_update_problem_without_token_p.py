# Developed By John Wick
import requests
import pytest

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def base_url():
    return BASE_URL

@pytest.fixture(scope="module")
def problem_id():
    # Use a placeholder problem ID; the test focuses on authentication, not existence
    return 1

def test_tc007_update_problem_without_token(base_url, problem_id):
    """
    Test Case TC007: Update problem without token (PUT)
    """
    url = f"{base_url}/problems/{problem_id}"
    payload = {
        "title": "Updated Title",
        "difficulty": "Hard"
    }
    # Send PUT request without Authorization header
    response = requests.put(url, json=payload)

    # Assert that the status code is 401 Unauthorized
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"

    # Attempt to parse JSON response
    try:
        data = response.json()
    except ValueError:
        data = {}

    # Assert that the response contains an error message
    assert any(key in data for key in ("msg", "error", "message")), "Response JSON does not contain an error message"

    # Verify that the error message indicates missing or invalid token
    error_msg = data.get("msg") or data.get("error") or data.get("message") or ""
    assert "token" in error_msg.lower() or "unauthorized" in error_msg.lower(), f"Unexpected error message: {error_msg}"