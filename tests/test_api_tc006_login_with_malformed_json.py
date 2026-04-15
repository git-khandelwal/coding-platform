import pytest
import requests

# NOTE: The base URL is assumed to be provided via environment or config.
# If not available, this will need to be updated to the actual service URL.
BASE_URL = "http://localhost:5000"

@pytest.fixture
def login_url():
    return f"{BASE_URL}/login"

def test_login_with_malformed_json(login_url):
    """
    TC006: Verify that login fails when request body is not valid JSON.
    """
    # Malformed JSON string (missing closing brace)
    malformed_data = '{"username": "testuser", "password": "password123"'
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        login_url, 
        data=malformed_data, 
        headers=headers
    )
    
    # Expected Result: 400 Bad Request
    assert response.status_code == 400, f"Expected 400, but got {response.status_code}"