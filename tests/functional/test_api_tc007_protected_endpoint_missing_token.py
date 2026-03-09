import os
import requests
import pytest


@pytest.fixture(scope="session")
def base_url() -> str:
    """
    Base URL for the API under test.
    Can be overridden by setting the BASE_URL environment variable.
    """
    return os.getenv("BASE_URL", "http://localhost:5000")


def test_protected_endpoint_missing_token(base_url: str) -> None:
    """
    TC007: Protected Endpoint – Missing Token
    Verify that accessing /protected without an Authorization header
    returns a 401 Unauthorized status and an error message in the JSON response.
    """
    url = f"{base_url}/protected"
    response = requests.get(url)

    # Assert the status code is 401 Unauthorized
    assert response.status_code == 401, (
        f"Expected status code 401, got {response.status_code}"
    )

    # Assert the response body contains an error message
    try:
        data = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")

    assert any(key in data for key in ("msg", "error")), (
        "Response JSON does not contain an error message key"
    )