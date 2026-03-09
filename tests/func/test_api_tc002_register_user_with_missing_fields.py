import pytest
import requests

BASE_URL = "http://localhost:5000"  # Adjust as needed for your environment

@pytest.fixture(scope="module")
def registration_url():
    return f"{BASE_URL}/register"

@pytest.mark.parametrize(
    "payload,missing_field",
    [
        ({"password": "somepassword"}, "username"),
        ({"username": "someuser"}, "password"),
    ]
)
def test_register_user_with_missing_fields(registration_url, payload, missing_field):
    response = requests.post(registration_url, json=payload)
    assert response.status_code == 400, f"Expected 400 Bad Request when {missing_field} is missing, got {response.status_code}"
    response_json = response.json()
    assert "error" in response_json, f"Expected 'error' in response when {missing_field} is missing"
    assert response_json["error"] == "Username and password are required", f"Expected error message for missing {missing_field}, got: {response_json['error']}"