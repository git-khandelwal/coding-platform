import os
import pytest
import requests


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the API under test."""
    return os.getenv("API_BASE_URL", "http://localhost:5000")


@pytest.fixture
def client():
    """Requests session fixture."""
    with requests.Session() as session:
        yield session


def test_tc002_protected_endpoint_without_jwt(base_url, client):
    """
    TC002: Verify access to protected endpoint without JWT.
    Sends a GET request to /protected without an Authorization header
    and asserts that the response is a 401 with an appropriate error message.
    """
    url = f"{base_url}/protected"
    response = client.get(url)

    # Expected HTTP status
    assert response.status_code == 401, f"Expected status code 401, got {response.status_code}"

    # Expected error indication in response body
    body_lower = response.text.lower()
    assert (
        "missing" in body_lower or "invalid" in body_lower or "token" in body_lower
    ), "Response body does not indicate missing or invalid token"