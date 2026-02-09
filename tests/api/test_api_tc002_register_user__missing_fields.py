import pytest
import requests

BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="module")
def base_url() -> str:
    """Return the base URL for the API."""
    return BASE_URL


@pytest.fixture(scope="session")
def http_session() -> requests.Session:
    """Provide a session object for HTTP requests."""
    with requests.Session() as session:
        yield session


def test_register_user_missing_fields(base_url: str, http_session: requests.Session) -> None:
    """
    TC002 – Register User – Missing Fields
    Verify that registration fails when required fields are omitted.
    """
    url = f"{base_url}/register"
    payload = {"username": "testuser"}  # Only username, no password

    response = http_session.post(url, json=payload)

    # Assert status code
    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"

    # Assert response body
    try:
        data = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")

    assert "error" in data, "Response JSON should contain an 'error' key"
    expected_error = "Username and password are required"
    assert data["error"] == expected_error, (
        f"Expected error message '{expected_error}', got '{data.get('error')}'"
    )