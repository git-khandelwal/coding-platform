import pytest
import requests

@pytest.fixture(scope="module")
def api_base_url():
    # GAP: The API base URL is not specified in the provided context.
    # Please set the correct base URL for your environment.
    return "http://localhost:5000"

@pytest.fixture
def add_problem_endpoint(api_base_url):
    return f"{api_base_url}/problems/add"

def test_add_problem_unauthorized_returns_401(add_problem_endpoint):
    # Prepare minimal valid problem data
    problem_data = {
        "title": "Sample Problem",
        "description": "Sample description",
        "difficulty": "Easy",
        "input_format": "int n",
        "output_format": "int result",
        "sample_input": "1",
        "sample_output": "1",
        "sample_code": "print(1)",
        "constraints": "1 <= n <= 100"
    }

    response = requests.post(add_problem_endpoint, json=problem_data)
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"