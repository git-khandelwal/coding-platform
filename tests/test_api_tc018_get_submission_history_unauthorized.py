import pytest
import requests

# NOTE: The actual base URL and endpoint path must be configured for your environment.
# There is a gap here: The exact URL for "submission history" is not specified.
# Based on the code context, possible endpoints are:
#   - /submissions (GET)
#   - /problems/<int:problem_id>/submissions (GET)
# Since the test case does not specify a problem ID, we will use /submissions.

BASE_URL = "http://localhost:5000"
SUBMISSION_HISTORY_ENDPOINT = f"{BASE_URL}/submissions"

@pytest.fixture(scope="function", autouse=False)
def setup_and_teardown():
    # Setup logic if needed (none required for this test)
    yield
    # Teardown logic if needed (none required for this test)

def test_get_submission_history_unauthorized_returns_401(setup_and_teardown):
    response = requests.get(SUBMISSION_HISTORY_ENDPOINT)
    assert response.status_code == 401, (
        f"Expected status code 401 for unauthorized request, got {response.status_code}. "
        f"Response body: {response.text}"
    )