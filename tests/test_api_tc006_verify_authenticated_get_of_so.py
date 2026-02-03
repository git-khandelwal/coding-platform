import os
import pytest
import requests

API_URL = os.getenv("API_URL", "http://localhost:5000")
LOGIN_ENDPOINT = f"{API_URL}/login"
SOLVE_ENDPOINT_TEMPLATE = f"{API_URL}/problems/{{problem_id}}/solve"

# Adjust these credentials to match a valid user in the test environment
TEST_USERNAME = os.getenv("TEST_USERNAME", "testuser")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "testpass")


@pytest.fixture(scope="session")
def auth_token():
    """Obtain a JWT for a known test user."""
    payload = {"username": TEST_USERNAME, "password": TEST_PASSWORD}
    response = requests.post(LOGIN_ENDPOINT, json=payload)
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    token = data.get("access_token") or data.get("token")
    assert token, "JWT token not found in login response"
    return token


@pytest.fixture(scope="session")
def known_problem_id():
    """Return a problem ID that is guaranteed to exist in the test database."""
    # In many test setups problem ID 1 is seeded; adjust if necessary.
    return 1


def test_solve_page_authenticated(auth_token, known_problem_id):
    """TC006 – Authenticated GET request to solve page should return 200 and contain a code editor."""
    url = SOLVE_ENDPOINT_TEMPLATE.format(problem_id=known_problem_id)
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(url, headers=headers)

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    # Simple heuristic: look for a textarea or a div with a known class used by the editor
    assert ("<textarea" in response.text.lower()) or ("code-editor" in response.text.lower()), \
        "Response does not contain expected code editor HTML"


def test_solve_page_unauthenticated(known_problem_id):
    """TC006 – Unauthenticated GET request to solve page should return 401 Unauthorized."""
    url = SOLVE_ENDPOINT_TEMPLATE.format(problem_id=known_problem_id)
    response = requests.get(url)  # No Authorization header

    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"