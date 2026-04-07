import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def registered_user_and_token():
    # Generate unique username for isolation
    username = f"testuser_tc022_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"

    # Register user
    register_resp = requests.post(
        f"{BASE_URL}/register",
        json={"username": username, "password": password}
    )
    assert register_resp.status_code == 201 or register_resp.status_code == 400

    # Login user
    login_resp = requests.post(
        f"{BASE_URL}/login",
        json={"username": username, "password": password}
    )
    assert login_resp.status_code == 200
    token = login_resp.json().get("access_token")
    assert token is not None

    yield token

    # No explicit teardown needed (user removal not specified)

@pytest.mark.usefixtures("registered_user_and_token")
def test_get_submission_history_problem_not_found(registered_user_and_token):
    # Use a very large problem_id that is unlikely to exist
    non_existent_problem_id = 999999

    headers = {
        "Authorization": f"Bearer {registered_user_and_token}"
    }

    resp = requests.get(
        f"{BASE_URL}/problems/{non_existent_problem_id}/submissions",
        headers=headers
    )

    assert resp.status_code == 404