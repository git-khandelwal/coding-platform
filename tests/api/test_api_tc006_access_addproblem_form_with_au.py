import os
import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def jwt_token():
    """
    Retrieve a valid JWT for an authenticated user.

    This fixture expects the token to be provided via the environment variable
    `TEST_JWT_TOKEN`. If the token cannot be obtained automatically (e.g., there
    is no public login endpoint in the current context), set the variable before
    running the tests.

    Returns
    -------
    str
        A JWT string suitable for the Authorization header.
    """
    token = os.getenv("TEST_JWT_TOKEN")
    if not token:
        pytest.fail(
            "JWT token not found. Set the environment variable TEST_JWT_TOKEN with a "
            "valid token for an authenticated user."
        )
    return token


@pytest.fixture
def auth_headers(jwt_token):
    """Headers containing the Authorization bearer token."""
    return {"Authorization": f"Bearer {jwt_token}"}


def test_tc006_access_add_problem_form_authenticated(auth_headers):
    """
    TC006 – Verify that an authenticated user can view the add‑problem form page.

    Steps:
    1. Send a GET request to the add‑problem endpoint with a valid JWT.
    2. Assert that the response status is 200 OK.
    3. Assert that the returned HTML contains the expected form fields.
    """
    url = f"{BASE_URL}/problems/add"
    response = requests.get(url, headers=auth_headers)

    # Expected Result 1: HTTP 200 OK
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    # Expected Result 2: HTML form with required fields
    html = response.text.lower()
    required_fields = ["name=\"title\"", "name=\"description\"", "name=\"difficulty\""]
    missing = [field for field in required_fields if field not in html]
    assert not missing, f"Missing expected form fields in response HTML: {missing}"