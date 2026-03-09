import uuid
import pytest
import requests

BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="session")
def user_credentials():
    """
    Create a unique user and obtain a JWT token.
    """
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "TestPass123!"

    # Register the user
    register_resp = requests.post(
        f"{BASE_URL}/register",
        json={"username": username, "password": password},
        timeout=5,
    )
    assert register_resp.status_code == 201, f"Registration failed: {register_resp.text}"

    # Login to get the token
    login_resp = requests.post(
        f"{BASE_URL}/login",
        json={"username": username, "password": password},
        timeout=5,
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json().get("access_token")
    assert token, "No access token received"

    return {"username": username, "token": token}


def test_protected_endpoint_valid_token(user_credentials):
    """
    TC006: Access `/protected` with a valid JWT.
    """
    headers = {"Authorization": f"Bearer {user_credentials['token']}"}
    resp = requests.get(f"{BASE_URL}/protected", headers=headers, timeout=5)

    assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}"
    data = resp.json()
    assert "logged_in_as" in data, "Response JSON missing 'logged_in_as'"
    assert (
        data["logged_in_as"] == user_credentials["username"]
    ), f"Expected logged_in_as to be '{user_credentials['username']}', got '{data['logged_in_as']}'"