import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="function")
def unique_user_credentials():
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "ValidPass123!"
    return {"username": unique_username, "password": password}

def test_register_new_user_tc001(unique_user_credentials):
    url = f"{BASE_URL}/register"
    payload = {
        "username": unique_user_credentials["username"],
        "password": unique_user_credentials["password"]
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
    assert response.headers.get("Content-Type", "").startswith("application/json")
    response_json = response.json()
    assert "message" in response_json, "Response JSON does not contain 'message'"
    assert response_json["message"] == "User registered successfully", f"Expected message 'User registered successfully', got '{response_json['message']}'"