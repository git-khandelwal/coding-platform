import pytest
import requests

BASE_URL = "http://localhost:5000"  # Update as appropriate for your environment

@pytest.fixture(scope="module")
def test_problem_id():
    """
    Fixture to create a problem and yield its ID, then clean up after test.
    Assumes /problems/add endpoint exists and requires authentication.
    If authentication is required, this fixture will need to be updated.
    """
    # WARNING: This assumes /problems/add does NOT require authentication.
    # If authentication is required, this fixture will need to be updated to obtain a token.
    problem_data = {
        "title": "Test Problem TC009",
        "description": "Test description for TC009.",
        "difficulty": "Easy",
        "input_format": "int n",
        "output_format": "int result",
        "sample_input": "1",
        "sample_output": "2",
        "sample_code": "print(2)",
        "constraints": "1 <= n <= 10"
    }
    add_url = f"{BASE_URL}/problems/add"
    # Try POST as JSON, fallback to form if needed
    response = requests.post(add_url, json=problem_data)
    assert response.status_code == 201, f"Setup failed: {response.status_code} {response.text}"
    # Try to get the new problem's ID from the response, fallback to listing all problems
    resp_json = response.json()
    problem_id = None
    if "problem" in resp_json and "id" in resp_json["problem"]:
        problem_id = resp_json["problem"]["id"]
    else:
        # Fallback: get all problems, find the one with our title
        list_url = f"{BASE_URL}/problems"
        list_response = requests.get(list_url)
        assert list_response.status_code == 200, "Failed to list problems for setup."
        # Try to parse HTML to find the problem ID (not ideal, but no API context for listing as JSON)
        # This is a gap: Without a JSON listing endpoint, cannot reliably extract problem ID.
        pytest.skip("Cannot determine created problem ID from /problems/add or /problems endpoints.")
    yield problem_id
    # Teardown: delete the problem if possible (requires authentication, not implemented here)

@pytest.mark.usefixtures("test_problem_id")
def test_get_problem_details_valid_id(test_problem_id):
    """
    TC009: Test retrieving details of a specific problem with valid ID.
    """
    if test_problem_id is None:
        pytest.skip("Problem ID could not be determined in setup.")
    url = f"{BASE_URL}/problems/{test_problem_id}"
    response = requests.get(url)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type or "html" in content_type, f"Expected HTML response, got Content-Type: {content_type}"
    # Optionally check for problem title in HTML
    assert "Test Problem TC009" in response.text, "Problem details HTML does not contain expected problem title."