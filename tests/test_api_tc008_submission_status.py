import pytest
import requests

# NOTE: The following details are missing and assumed for the test environment:
# 1. BASE_URL: The URL where the application is hosted.
# 2. AUTH_TOKEN: A valid JWT token for an authenticated user.
# 3. PROBLEM_ID: A valid problem ID existing in the database.
# 4. CODE_SNIPPET: A valid code string to submit.

BASE_URL = "http://localhost:5000"
AUTH_TOKEN = "YOUR_JWT_TOKEN_HERE"
PROBLEM_ID = 1
CODE_SNIPPET = "def solve(): return True"

@pytest.fixture
def headers():
    return {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

def test_submission_status_tracking(headers):
    """
    TC008: Verify that code submissions are tracked with status updates.
    """
    # 1. Submit code for a specific problem
    submit_url = f"{BASE_URL}/problems/{PROBLEM_ID}/solve"
    payload = {"code": CODE_SNIPPET}
    
    response = requests.post(submit_url, json=payload, headers=headers)
    assert response.status_code == 200, f"Submission failed with status {response.status_code}"
    
    # 2. Check submission history
    history_url = f"{BASE_URL}/problems/{PROBLEM_ID}/submissions"
    history_response = requests.get(history_url, headers=headers)
    assert history_response.status_code == 200, "Failed to retrieve submission history"
    
    submissions = history_response.json()
    assert len(submissions) > 0, "Submission history is empty"
    
    # Verify the most recent submission status
    latest_submission = submissions[0]
    valid_statuses = ["Pending", "Success", "Failed", "Error"]
    
    assert "status" in latest_submission, "Status field missing in submission history"
    assert latest_submission["status"] in valid_statuses, \
        f"Expected status to be one of {valid_statuses}, but got {latest_submission['status']}"