import os
import pytest
import requests

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")
LOGIN_ENDPOINT = os.getenv("API_LOGIN_ENDPOINT", "/login")
USERNAME = os.getenv("API_TEST_USERNAME", "testuser")
PASSWORD = os.getenv("API_TEST_PASSWORD", "testpass")
PROBLEM_ID = int(os.getenv("API_TEST_PROBLEM_ID", "1"))


@pytest.fixture(scope="session")
def auth_token():
    """
    Obtain a JWT token using the login endpoint.
    Adjust the payload and endpoint as needed for the target application.
    """
    login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
    payload = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(login_url, json=payload)
    assert response.status_code == 200, f"Login failed with status {response.status_code}"
    data = response.json()
    token = data.get("access_token") or data.get("token")
    assert token, "JWT token not found in login response"
    return token


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


def test_tc011_retrieval_of_submission_history_authenticated(auth_headers):
    """
    TC011: Verify retrieval of submission history (authenticated)
    """
    url = f"{BASE_URL}/problems/{PROBLEM_ID}/submissions"
    response = requests.get(url, headers=auth_headers)

    # Expected Result 1: HTTP 200
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Expected Result 2: Response is a JSON array
    try:
        json_data = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")

    assert isinstance(json_data, list), f"Expected JSON array, got {type(json_data)}"

    # Expected Result 3: Each element contains required fields
    required_fields = {"problem_title", "status", "result", "timestamp", "code"}
    for idx, entry in enumerate(json_data):
        assert isinstance(entry, dict), f"Entry {idx} is not a JSON object"
        missing = required_fields - entry.keys()
        assert not missing, f"Entry {idx} missing fields: {missing}"
        # Optional: basic type checks
        assert isinstance(entry["problem_title"], str)
        assert isinstance(entry["status"], str)
        assert isinstance(entry["result"], (str, type(None)))
        assert isinstance(entry["timestamp"], str)
        assert isinstance(entry["code"], str)