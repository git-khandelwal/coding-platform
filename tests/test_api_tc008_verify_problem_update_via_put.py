import pytest
import requests


@pytest.fixture(scope="session")
def base_url():
    # Adjust the base URL as needed for the test environment
    return "http://localhost:5000"


@pytest.fixture(scope="session")
def auth_token(base_url):
    """
    Obtain a valid JWT for an existing test user.
    Adjust the login endpoint and credentials according to the application.
    """
    login_endpoint = f"{base_url}/login"
    credentials = {"username": "testuser", "password": "testpass"}
    resp = requests.post(login_endpoint, json=credentials)
    assert resp.status_code == 200, f"Login failed with status {resp.status_code}"
    data = resp.json()
    token = data.get("access_token") or data.get("token")
    assert token, "JWT token not found in login response"
    return token


@pytest.fixture
def original_difficulty(base_url, auth_token):
    """
    Capture the original difficulty of problem ID 1 so it can be restored after the test.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = requests.get(f"{base_url}/problems/1", headers=headers)
    assert resp.status_code == 200, f"Failed to fetch problem before test, status {resp.status_code}"
    try:
        problem_data = resp.json()
        difficulty = problem_data.get("difficulty")
    except ValueError:
        difficulty = None  # Non‑JSON response; cannot capture original value
    yield difficulty
    # Teardown: revert the difficulty if it was changed and we captured a value
    if difficulty and difficulty != "Hard":
        requests.put(
            f"{base_url}/problems/1",
            headers=headers,
            json={"difficulty": difficulty},
        )


def test_tc008_update_problem_difficulty(base_url, auth_token, original_difficulty):
    """
    TC008 – Verify problem update via PUT (valid data)
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    update_payload = {"difficulty": "Hard"}

    # Step 3: Send PUT request to update the problem
    put_resp = requests.put(f"{base_url}/problems/1", headers=headers, json=update_payload)
    assert put_resp.status_code == 200, f"PUT returned unexpected status {put_resp.status_code}"
    put_body = put_resp.json()
    assert put_body.get("message") == "Problem updated successfully", "Unexpected response message"

    # Step 5: Retrieve the problem to confirm the change
    get_resp = requests.get(f"{base_url}/problems/1", headers=headers)
    assert get_resp.status_code == 200, f"GET after update returned status {get_resp.status_code}"
    try:
        problem_data = get_resp.json()
        assert problem_data.get("difficulty") == "Hard", "Difficulty was not updated to 'Hard'"
    except ValueError:
        pytest.fail("GET response is not JSON; cannot verify updated difficulty")