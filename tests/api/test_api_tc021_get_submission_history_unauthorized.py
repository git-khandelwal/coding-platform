import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def problem_id():
    # GAP: No endpoint or method provided to create or retrieve a valid problem ID without authentication.
    # This fixture assumes a problem with ID 1 exists in the system as per the test case precondition.
    return 1

def test_get_submission_history_unauthorized(problem_id):
    """
    TC021: Get Submission History (Unauthorized)
    Test retrieving submission history without authentication.
    Expected: Response status is 401 Unauthorized.
    """
    url = f"{BASE_URL}/problems/{problem_id}/submissions"
    response = requests.get(url)
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"