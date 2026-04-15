import pytest
import requests
import os

# NOTE: Missing details: 
# 1. Base URL for the API is not provided in context.
# 2. Authentication token generation logic is not provided.
# 3. Valid problem_id for testing is not provided.
# 4. Valid code snippet for the specific problem is not provided.

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

@pytest.fixture
def auth_token():
    # Placeholder for authentication logic
    # In a real scenario, this would perform a login request
    return "YOUR_JWT_TOKEN"

@pytest.fixture
def headers(auth_token):
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

def test_code_submission_evaluation(headers):
    """
    TC008: Verify that submitted code is evaluated and returns a status.
    """
    # 1. Select a problem (Assuming problem_id 1 exists)
    problem_id = 1
    
    # 2. Input code solution
    payload = {
        "code": "def solve(): return 'Hello World'"
    }
    
    # 3. Submit the solution
    endpoint = f"{BASE_URL}/problems/{problem_id}/solve"
    response = requests.post(endpoint, json=payload, headers=headers)
    
    # Expected Result Assertions
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert "status" in data, "Response missing 'status' field"
    assert data["status"] in ["Success", "Failed", "Error"], f"Unexpected status: {data['status']}"
    assert "result" in data, "Response missing 'result' field"
    assert data["message"] == "Submission evaluated"