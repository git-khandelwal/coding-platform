import pytest
import requests

@pytest.fixture(scope="module")
def base_url():
    # GAP: Base URL for the API is not provided in the context.
    # Please provide the API base URL (e.g., http://localhost:5000 or similar).
    raise NotImplementedError("Base URL for the API is not specified. Please provide the API server address.")

@pytest.fixture(scope="function")
def register_endpoint(base_url):
    return f"{base_url}/register"

@pytest.mark.parametrize(
    "payload,missing_field",
    [
        ({"password": "testpass"}, "username"),
        ({"username": "testuser"}, "password"),
        ({}, "both"),
    ]
)
def test_register_missing_fields_returns_error(register_endpoint, payload, missing_field):
    response = requests.post(register_endpoint, json=payload)
    assert response.status_code == 400, f"Expected status code 400 for missing {missing_field}, got {response.status_code}"
    try:
        data = response.json()
    except Exception:
        pytest.fail(f"Response is not valid JSON: {response.text}")
    assert "error" in data, f"Expected 'error' key in response for missing {missing_field}, got {data}"
    assert data["error"] == "Username and password are required", f"Expected error message for missing {missing_field}, got: {data['error']}"