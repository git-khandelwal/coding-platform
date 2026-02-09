import os
import uuid
import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def session():
    """Reusable requests session."""
    return requests.Session()


@pytest.fixture(scope="session")
def register_user(session):
    """Register a new user and return credentials."""
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "TestPass123!"
    payload = {"username": username, "password": password}
    resp = session.post(f"{BASE_URL}/register", json=payload)
    resp.raise_for_status()
    return {"username": username, "password": password}


@pytest.fixture(scope="session")
def auth_token(session, register_user):
    """Login and retrieve JWT token."""
    payload = {
        "username": register_user["username"],
        "password": register_user["password"],
    }
    resp = session.post(f"{BASE_URL}/login", json=payload)
    resp.raise_for_status()
    token = resp.json().get("access_token")
    assert token, "No access token returned"
    return token


@pytest.fixture(scope="session")
def problem_id(session, auth_token):
    """Create a problem and return its ID."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "title": "Sample Problem",
        "description": "Return the string 'Correct' when executed.",
        "test_cases": [
            {"input": "", "expected_output": "Correct"}
        ],
    }
    resp = session.post(f"{BASE_URL}/problems", json=payload, headers=headers)
    resp.raise_for_status()
    problem = resp.json()
    pid = problem.get("id")
    assert pid, "Problem ID not returned"
    yield pid
    # Teardown: attempt to delete the problem if endpoint exists
    session.delete(f"{BASE_URL}/problems/{pid}", headers=headers)


def test_submit_solution_success(session, auth_token, problem_id):
    """TC008: Verify that a solution can be submitted and evaluated successfully."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Provide code that should pass the sample problem
    code = """
def solve():
    return "Correct"
"""
    payload = {"code": code}
    url = f"{BASE_URL}/problems/{problem_id}/solve"
    resp = session.post(url, json=payload, headers=headers)

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data.get("message") == "Submission evaluated", "Incorrect message"
    assert data.get("status") == "Success", "Status not Success"
    assert data.get("result") == "Correct", "Result not Correct"
    # Optional: check that user_print is present if applicable
    assert "user_print" in data, "user_print missing in response"
    # Ensure no error in response
    assert "error" not in data, f"Unexpected error in response: {data.get('error')}"