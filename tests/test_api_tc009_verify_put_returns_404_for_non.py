import os
import pytest
import requests


@pytest.fixture(scope="session")
def base_url():
    """Base URL of the API under test."""
    return os.getenv("BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def auth_token(base_url):
    """
    Obtain a valid JWT for an existing test user.
    Assumes an authentication endpoint at /login that returns a JSON payload
    containing either ``access_token`` or ``token``.
    """
    login_url = f"{base_url}/login"
    credentials = {
        "username": os.getenv("TEST_USERNAME", "testuser"),
        "password": os.getenv("TEST_PASSWORD", "testpass"),
    }
    resp = requests.post(login_url, json=credentials)
    assert resp.status_code == 200, f"Login failed with status {resp.status_code}"
    data = resp.json()
    token = data.get("access_token") or data.get("token")
    assert token, "JWT token not found in login response"
    return token


def test_put_nonexistent_problem_returns_404(base_url, auth_token):
    """
    TC009 – Verify PUT returns 404 for non‑existent problem.
    """
    nonexistent_id = 9999
    url = f"{base_url}/problems/{nonexistent_id}"
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "title": "Updated Title",
        "description": "Updated description",
        "difficulty": "Hard",
    }

    response = requests.put(url, json=payload, headers=headers)

    # Expected: 404 Not Found
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    # Verify response body indicates the problem does not exist
    try:
        body = response.json()
    except ValueError:
        body = response.text

    body_str = str(body).lower()
    assert ("not found" in body_str) or ("does not exist" in body_str) or ("no such" in body_str), (
        "Response body does not clearly indicate a missing problem"
    )