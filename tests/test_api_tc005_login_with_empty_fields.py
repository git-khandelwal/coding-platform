import pytest
import requests

# NOTE: The provided API code for /login does not explicitly handle empty fields 
# with a 400 error; it currently queries the database with the provided values.
# This test assumes the API should return 400 for empty inputs as per the Test Case requirements.

BASE_URL = "http://localhost:5000"

@pytest.fixture
def login_url():
    return f"{BASE_URL}/login"

@pytest.mark.parametrize("payload", [
    {"username": "", "password": "password123"},
    {"username": "testuser", "password": ""},
    {"username": "", "password": ""}
])
def test_login_with_empty_fields(login_url, payload):
    """
    TC005: Verify that login fails when username or password fields are empty.
    Expected Result: 400 Bad Request error returned.
    """
    response = requests.post(login_url, json=payload)
    
    # Assert that the login fails with a 400 Bad Request status code
    assert response.status_code == 400, f"Expected 400, but got {response.status_code}. Response: {response.text}"