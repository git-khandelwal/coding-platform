import os
import re

import pytest
import requests


@pytest.fixture(scope="session")
def base_url():
    """
    Base URL for the API. Defaults to http://localhost:5000 but can be overridden
    by setting the environment variable API_BASE_URL.
    """
    return os.getenv("API_BASE_URL", "http://localhost:5000")


def test_protected_endpoint_invalid_token(base_url):
    """
    TC008: Protected Endpoint – Invalid Token
    Verify that accessing /protected with an invalid or expired token returns
    a 401 Unauthorized response and an error message indicating the token is
    invalid or expired.
    """
    url = f"{base_url.rstrip('/')}/protected"
    headers = {"Authorization": "Bearer invalidtoken"}

    response = requests.get(url, headers=headers)

    # Assert status code is 401 Unauthorized
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    # Attempt to parse JSON response
    try:
        data = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")

    # The API should return an error message. Accept common keys.
    error_keys = {"error", "msg", "message"}
    assert any(key in data for key in error_keys), (
        f"Response JSON does not contain an error key. Received: {data}"
    )

    # Ensure the error message indicates an invalid or expired token
    error_message = next(
        (data[key] for key in error_keys if key in data), ""
    )
    assert isinstance(error_message, str), "Error message is not a string"
    assert re.search(r"(invalid|expired)", error_message, re.IGNORECASE), (
        f"Error message does not mention 'invalid' or 'expired': {error_message}"
    )