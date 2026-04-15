import pytest
import requests

# NOTE: The provided code context does not specify the base URL or authentication mechanism implementation.
# Assuming standard environment variables for configuration.
BASE_URL = "http://localhost:5000"

@pytest.fixture
def auth_token():
    """
    Fixture to obtain an authentication token.
    GAPS: Implementation details for login endpoint are missing from context.
    """
    login_data = {"username": "testuser", "password": "testpassword"}
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    assert response.status_code == 200
    return response.json().get("access_token")

def test_add_new_problem(auth_token):
    """
    TC007: Verify that an authenticated user can add a new coding problem.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    new_problem_data = {
        "title": "Test Problem Title",
        "description": "Test description",
        "difficulty": "Easy",
        "input_format": "Integer",
        "output_format": "Integer",
        "sample_input": "1",
        "sample_output": "2",
        "sample_code": "def solve(): pass",
        "constraints": "None"
    }

    # Step 1: Submit new problem details
    post_response = requests.post(
        f"{BASE_URL}/problems/add", 
        json=new_problem_data, 
        headers=headers
    )

    # Expected Result 1: Problem is saved to the database
    assert post_response.status_code == 201
    assert post_response.json().get("message") == "Problem added successfully"

    # Expected Result 2: Problem appears in the list
    # GAPS: The context shows /problems returns a rendered template, not JSON.
    # Assuming an API endpoint exists or is expected to return JSON for verification.
    get_response = requests.get(f"{BASE_URL}/problems")
    
    # If /problems returns HTML, this assertion will fail. 
    # Verification assumes an API-compliant response format.
    assert get_response.status_code == 200
    assert new_problem_data["title"] in get_response.text