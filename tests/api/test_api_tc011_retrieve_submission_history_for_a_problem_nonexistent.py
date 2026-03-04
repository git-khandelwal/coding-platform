import os
import requests
import pytest

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def auth_token():
    """
    Fixture to provide a valid JWT token.
    The token must be supplied via the JWT_TOKEN environment variable.
    """
    token = os.getenv("JWT_TOKEN")
    if not token:
        pytest.skip("JWT_TOKEN environment variable not set. Skipping test.")
    return token


@pytest.fixture(scope="session")
def base_url():
    """
    Fixture to provide the base URL for the API.
    """
    return BASE_URL


def test_submission_history_nonexistent_problem(base_url, auth_token):
    """
    TC011: Retrieve submission history for a problem (non‑existent)

    Test that a GET request to the submission history endpoint returns 404
    for an invalid problem ID and that the JSON body contains an error message.
    """
    # Choose a problem ID that is highly unlikely to exist
    non_existent_id = 999999

    url = f"{base_url}/problems/{non_existent_id}/submissions"
    headers = {"Authorization": f"Bearer {auth_token}"}

    response = requests.get(url, headers=headers)

    assert response.status_code == 404, (
        f"Expected status code 404, got {response.status_code}"
    )

    try:
        data = response.json()
    except ValueError:
        pytest.fail("Response body is not valid JSON")

    assert isinstance(data, dict), f"Expected JSON object, got {type(data)}"

    # The API should return an error message in the JSON body
    assert (
        "message" in data or "error" in data
    ), "JSON response does not contain 'message' or 'error' key"