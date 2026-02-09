import uuid
import pytest
import requests

BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL for the API."""
    return BASE_URL


@pytest.fixture(scope="session")
def auth_token(base_url: str) -> str:
    """
    Register a new user and obtain a JWT access token.
    The user credentials are unique for each test run.
    """
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "TestPass123!"

    # Register the user
    register_resp = requests.post(
        f"{base_url}/register",
        json={"username": username, "password": password},
    )
    assert register_resp.status_code == 201, f"Registration failed: {register_resp.text}"

    # Login to get JWT token
    login_resp = requests.post(
        f"{base_url}/login",
        json={"username": username, "password": password},
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json().get("access_token")
    assert token, "No access token returned after login"
    return token


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """Return headers with the JWT token for authenticated requests."""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }


def test_add_problem_success(base_url: str, auth_headers: dict) -> None:
    """
    TC006: Add Problem – Success
    Verify that an authenticated user can create a new problem.
    """
    problem_payload = {
        "title": "Two Sum",
        "description": "Find two numbers that add up to the target sum.",
        "difficulty": "Easy",
        "tags": ["array", "hash-table"],
    }

    # Send POST request to create a new problem
    response = requests.post(
        f"{base_url}/problems",
        json=problem_payload,
        headers=auth_headers,
    )

    # Assertions based on Expected Result
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    resp_json = response.json()
    assert (
        resp_json.get("message") == "Problem added successfully"
    ), f"Unexpected message: {resp_json.get('message')}"

    # The response should contain the created problem data
    created_problem = resp_json.get("problem") or resp_json.get("data") or resp_json
    assert created_problem, "No problem data returned in response"

    # Validate returned problem fields
    assert created_problem.get("title") == problem_payload["title"]
    assert created_problem.get("description") == problem_payload["description"]
    assert created_problem.get("difficulty") == problem_payload["difficulty"]
    assert created_problem.get("tags") == problem_payload["tags"]

    # Optional cleanup: delete the created problem (if DELETE endpoint exists)
    problem_id = created_problem.get("id")
    if problem_id:
        delete_resp = requests.delete(
            f"{base_url}/problems/{problem_id}",
            headers=auth_headers,
        )
        # The delete operation may return 200 or 204; ignore status for cleanup
        _ = delete_resp.status_code
    """