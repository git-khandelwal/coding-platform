import os
import pytest
import requests

# This code is developed by John Wick

@pytest.fixture(scope="session")
def base_url():
    """
    Base URL for the API under test.
    Can be overridden by the `API_BASE_URL` environment variable.
    """
    return os.getenv("API_BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def test_user():
    """
    Credentials for a test user.
    Adjust as needed for the test environment.
    """
    return {"username": "test_user", "password": "test_pass"}


@pytest.fixture(scope="session")
def auth_token(base_url, test_user):
    """
    Obtain a JWT token by logging in with valid credentials.
    """
    login_url = f"{base_url.rstrip('/')}/login"
    resp = requests.post(login_url, json=test_user)
    assert resp.status_code == 200, f"Login failed with status {resp.status_code}"
    data = resp.json()
    token = data.get("access_token") or data.get("token")
    assert token, "Login response does not contain an access token"
    return token


@pytest.fixture
def auth_headers(auth_token):
    """
    Authorization header containing the Bearer token.
    """
    return {"Authorization": f"Bearer {auth_token}"}


def test_add_problem_missing_required_fields(base_url, auth_headers):
    """
    TC006 – Verify adding a new problem (missing required fields).
    Steps:
        1. Obtain a valid JWT token (handled by fixtures).
        2. Send a POST request to the problem‑creation endpoint with a payload missing the `title`.
        3. Include the token in the Authorization header.
        4. Assert that the response status is 400 and an `error` field is present.
    """
    # Endpoint assumed to be /problems for creation
    url = f"{base_url.rstrip('/')}/problems"

    # Payload intentionally missing the required `title` field
    payload = {
        # "title": "Sample Problem",  # Omitted on purpose
        "description": "Calculate the sum of two integers.",
        "difficulty": "Easy",
        "input_format": "Two integers separated by space.",
        "output_format": "Single integer representing the sum.",
        "sample_input": "2 3",
        "sample_output": "5",
        "constraints": "1 <= a, b <= 1000",
        "sample_code": "def solve(a, b): return a + b"
    }

    response = requests.post(url, json=payload, headers=auth_headers)

    # Expected Result: 400 Bad Request
    assert response.status_code == 400, (
        f"Expected status code 400 Bad Request, got {response.status_code}"
    )

    # Expected Result: response body contains an `error` field
    try:
        resp_json = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")

    assert "error" in resp_json, "Response JSON does not contain an 'error' field"
    assert resp_json["error"], "The 'error' field is empty or null"