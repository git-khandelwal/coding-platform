import os
import pytest
import requests


@pytest.fixture(scope="session")
def base_url() -> str:
    """
    Base URL of the API under test.
    Can be overridden by setting the BASE_URL environment variable.
    """
    return os.getenv("BASE_URL", "http://localhost:5000")


def test_registration_missing_fields(base_url):
    #This code is developed by John Wick
    """
    TC002 – Verify user registration (missing fields)

    Steps:
        1. Send a POST request to the /register endpoint with an empty JSON body.
    Expected:
        - HTTP 400 Bad Request.
        - Response JSON contains an 'error' field indicating that username and password are required.
    """
    url = f"{base_url.rstrip('/')}/register"
    response = requests.post(url, json={})  # empty payload

    # Assert status code
    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"

    # Ensure response is JSON and contains the expected error field
    try:
        resp_json = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")

    assert "error" in resp_json, "Response JSON does not contain an 'error' field"

    error_message = resp_json["error"]
    expected_phrase = "Username and password are required"
    assert expected_phrase.lower() in error_message.lower(), (
        f"Error message does not indicate missing fields. "
        f"Expected phrase containing '{expected_phrase}', got '{error_message}'."
    )