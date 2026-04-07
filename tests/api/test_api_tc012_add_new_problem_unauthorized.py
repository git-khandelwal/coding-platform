import pytest
import requests

@pytest.fixture(scope="module")
def api_base_url():
    # GAP: API base URL is not specified in the provided context.
    # Please provide the API base URL (e.g., http://localhost:5000 or similar).
    pytest.skip("API base URL is not specified in the test context.")

@pytest.fixture
def sample_problem_payload():
    # Example payload for adding a problem; field names based on code context.
    return {
        "title": "Sample Problem",
        "description": "Solve X + Y",
        "difficulty": "Easy",
        "input_format": "Two integers X and Y",
        "output_format": "Sum of X and Y",
        "sample_input": "1 2",
        "sample_output": "3",
        "sample_code": "print(sum(map(int, input().split())))",
        "constraints": "1 <= X, Y <= 1000"
    }

def test_add_new_problem_unauthorized(api_base_url, sample_problem_payload):
    """
    TC012: Add New Problem (Unauthorized)
    Test adding a new problem without authentication.
    Expected: Response status is 401 Unauthorized.
    """
    url = f"{api_base_url}/problems/add"
    response = requests.post(url, json=sample_problem_payload)
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"