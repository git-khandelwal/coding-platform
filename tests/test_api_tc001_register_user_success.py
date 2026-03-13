import pytest
import requests

@pytest.fixture(scope="function")
def base_url():
    # NOTE: The API host/port is not specified in the context.
    # Please set the correct base URL for your environment.
    # Example: "http://localhost:5000"
    pytest.skip("Base URL for API is not provided in the context. Please specify the API host/port.")

@pytest.fixture(scope="function")
def registration_payload():
    return {
        "username": "test",
        "password": "1234"
    }

def test_register_user_success(base_url, registration_payload):
    url = f"{base_url}/register"
    response = requests.post(url, json=registration_payload)
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
    resp_json = response.json()
    assert "message" in resp_json, "Response JSON does not contain 'message'"
    assert resp_json["message"] == "User registered successfully", f"Expected message 'User registered successfully', got '{resp_json['message']}'"