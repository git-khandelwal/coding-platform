import os
import pytest
import requests

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def problem_id():
    """
    Attempt to retrieve an existing problem ID.
    The test will be skipped if no problem is found.
    """
    # Try a few common IDs; adjust as needed for the actual system.
    for candidate in range(1, 6):
        url = f"{BASE_URL}/problems/{candidate}"
        resp = requests.get(url)
        if resp.status_code == 200:
            return candidate
    pytest.skip("No existing problem found for testing.")


def test_solve_interface_unauthenticated(problem_id):
    """
    TC009: Retrieve solve interface for a problem (unauthenticated)
    """
    url = f"{BASE_URL}/problems/{problem_id}/solve"
    # No Authorization header
    response = requests.get(url)

    # Expected: 401 Unauthorized
    assert response.status_code == 401, (
        f"Expected status 401, got {response.status_code}. "
        f"Response body: {response.text}"
    )

    # Expected: JSON body contains an error message
    try:
        data = response.json()
    except ValueError:
        pytest.fail(f"Response is not JSON: {response.text}")

    # Flask-JWT-Extended typically returns a 'msg' key for errors
    assert "msg" in data, (
        f"Expected 'msg' key in error response, got {data}"
    )
    assert isinstance(data["msg"], str) and data["msg"], (
        f"Error message should be a non-empty string, got {data['msg']}"
    )