import uuid
import pytest
import requests

BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="session")
def user_credentials():
    """Generate unique user credentials for the test session."""
    return {
        "username": f"testuser_{uuid.uuid4().hex[:8]}",
        "password": "TestPass123!"
    }


@pytest.fixture(scope="session")
def register_user(user_credentials):
    """Register a new user and ensure the registration succeeds."""
    url = f"{BASE_URL}/register"
    response = requests.post(url, json=user_credentials)
    assert response.status_code == 201, f"Registration failed: {response.text}"
    return response.json()


@pytest.fixture(scope="session")
def auth_token(user_credentials):
    """Log in with the registered user and retrieve a JWT token."""
    url = f"{BASE_URL}/login"
    response = requests.post(url, json=user_credentials)
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data, "No access_token in login response"
    return data["access_token"]


@pytest.fixture(scope="session")
def problem_id(auth_token):
    """Create a problem that can be used for submission."""
    url = f"{BASE_URL}/problems"
    headers = {"Authorization": f"Bearer {auth_token}"}
    problem_payload = {
        "title": "Sample Problem",
        "description": "Just a test problem.",
        "difficulty": "Easy",
        "input_spec": "None",
        "output_spec": "None",
        "sample_input": "",
        "sample_output": ""
    }
    response = requests.post(url, json=problem_payload, headers=headers)
    assert response.status_code == 201, f"Problem creation failed: {response.text}"
    data = response.json()
    assert "id" in data, "Problem ID not returned"
    return data["id"]


def test_submit_solution_syntax_error(problem_id, auth_token):
    """
    TC009: Submit Solution – Syntax Error
    Verify that a solution with a syntax error is evaluated with status “Error”.
    """
    url = f"{BASE_URL}/problems/{problem_id}/solve"
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Intentionally malformed Python code
    code_with_error = "def faulty_func(:\n    pass"
    payload = {"code": code_with_error}

    response = requests.post(url, json=payload, headers=headers)

    # Expected status code 200
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    data = response.json()

    # Expected response body contains status "Error"
    assert "status" in data, "Response missing 'status' field"
    assert data["status"] == "Error", f"Expected status 'Error', got '{data['status']}'"

    # Expected an appropriate error message
    assert "result" in data, "Response missing 'result' field"
    assert isinstance(data["result"], str) and data["result"], "Result message is empty"

    # Optional: check that the error message mentions syntax
    assert "syntax" in data["result"].lower(), "Error message does not mention syntax error"