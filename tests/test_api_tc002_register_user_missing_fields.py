import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def register_url():
    return f"{BASE_URL}/register"

@pytest.mark.usefixtures("register_url")
class TestRegisterUserMissingFields:
    def test_register_missing_username(self, register_url):
        payload = {
            # 'username' is missing
            "password": "1234"
        }
        response = requests.post(register_url, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert response.json().get("error") == "Username and password are required"

    def test_register_missing_password(self, register_url):
        payload = {
            "username": "test"
            # 'password' is missing
        }
        response = requests.post(register_url, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert response.json().get("error") == "Username and password are required"