# Developed By John Wick
import pytest
import requests

BASE_URL = "http://localhost:5000"  # Adjust to your test environment

@pytest.fixture(scope="module")
def base_url():
    return BASE_URL

@pytest.fixture(scope="module")
def problem_id():
    # Assuming a problem with ID 1 exists in the test database
    return 1

def test_retrieve_specific_problem(base_url, problem_id):
    """
    TC002: Verify that a GET request for an existing problem ID returns detailed problem information.
    """
    url = f"{base_url}/problems/{problem_id}"
    response = requests.get(url, timeout=5)

    # Assert HTTP status code
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    # Assert response body is JSON
    try:
        data = response.json()
    except ValueError:
        pytest.fail("Response body is not valid JSON")

    # Required fields in the response
    required_fields = [
        "id",
        "title",
        "description",
        "difficulty",
        "input_format",
        "output_format",
        "sample_input",
        "sample_output",
        "constraints",
    ]

    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Verify that the returned id matches the requested problem_id
    assert data["id"] == problem_id, f"Expected id {problem_id}, got {data['id']}"