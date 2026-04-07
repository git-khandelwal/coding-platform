import os
import pytest
import requests

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
# Base URL of the API under test. Set the environment variable API_BASE_URL
# accordingly, e.g., http://localhost:5000
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

# Credentials for a user that exists in the system. These must be provided
# via environment variables; otherwise the fixture will raise an error.
USERNAME = os.getenv("API_TEST_USERNAME")
PASSWORD = os.getenv("API_TEST_PASSWORD")

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------
@pytest.fixture(scope="session")
def jwt_token():
    """
    Obtain a valid JWT for an existing user.

    The login endpoint and payload are not defined in the provided context.
    Adjust the URL, request method, and payload format to match the actual
    authentication implementation.
    """
    if not USERNAME or not PASSWORD:
        raise RuntimeError(
            "Authentication credentials not provided. Set API_TEST_USERNAME and "
            "API_TEST_PASSWORD environment variables."
        )

    login_url = f"{BASE_URL}/login"  # <-- Update if the login endpoint differs
    payload = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(login_url, json=payload)

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to obtain JWT. Login request returned {response.status_code}: {response.text}"
        )

    # The exact key containing the token depends on the implementation.
    # Common keys are 'access_token' or 'token'.
    token = response.json().get("access_token") or response.json().get("token")
    if not token:
        raise RuntimeError(
            "JWT not found in login response. Adjust the token extraction logic."
        )
    return token


@pytest.fixture(scope="session")
def valid_problem_id(jwt_token):
    """
    Retrieve an existing problem ID that can be used for the solve page.

    The endpoint to list or fetch problems is not fully specified.
    Adjust the request as needed to obtain a valid ID.
    """
    list_url = f"{BASE_URL}/problems"
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(list_url, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to retrieve problem list. Status {response.status_code}: {response.text}"
        )

    # Assuming the problems list endpoint returns HTML; we need a reliable way
    # to extract an ID. If a JSON API exists (e.g., /api/problems), replace the
    # parsing logic accordingly.
    # Placeholder: return a hard‑coded ID if known.
    # TODO: Implement proper extraction of a problem ID from the response.
    raise NotImplementedError(
        "Extraction of a valid problem ID is not implemented. Provide a method "
        "to obtain an existing problem ID (e.g., parse the HTML, call a JSON API, "
        "or use a known static ID)."
    )
    # Example static fallback (uncomment if appropriate):
    # return 1


# ----------------------------------------------------------------------
# Test case: TC008 – Access problem‑solve page with authentication
# ----------------------------------------------------------------------
def test_tc008_access_problem_solve_page_authenticated(jwt_token, valid_problem_id):
    """
    Verify that an authenticated user can open the problem‑solve interface
    for an existing problem.
    """
    solve_url = f"{BASE_URL}/problems/{valid_problem_id}/solve"
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(solve_url, headers=headers)

    # Expected Result 1: HTTP 200 OK
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    # Expected Result 2: HTML contains a code editor and problem description
    content = response.text.lower()
    assert "code editor" in content, "Response does not contain expected 'code editor' text"
    assert "problem description" in content, "Response does not contain expected 'problem description' text"