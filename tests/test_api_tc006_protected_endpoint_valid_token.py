import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="function")
def register_and_login():
    # Register user
    register_resp = requests.post(
        f"{BASE_URL}/register",
        json={"username": "test", "password": "1234"}
    )
    # Ignore 400 if user already exists
    assert register_resp.status_code in [201, 400]
    # Login user
    login_resp = requests.post(
        f"{BASE_URL}/login",
        json={"username": "test", "password": "1234"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json().get("access_token")
    assert token is not None
    return token

def test_protected_endpoint_valid_token_TC006(register_and_login):
    token = register_and_login
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/protected", headers=headers)
    assert resp.status_code == 200
    resp_json = resp.json()
    assert "logged_in_as" in resp_json
    assert resp_json["logged_in_as"] == "test"