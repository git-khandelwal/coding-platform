"""Shared fixtures for API tests."""
import pytest
import requests

from tests.lib.config import get_base_url, get_user_credentials


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the API under test. Use API_BASE_URL or BASE_URL env var."""
    return get_base_url()


@pytest.fixture(scope="session")
def user_credentials():
    """Valid user credentials for login. Use TEST_USERNAME / TEST_PASSWORD env to override."""
    return get_user_credentials()


@pytest.fixture(scope="session")
def auth_token(base_url, user_credentials):
    """Obtain a JWT token by logging in. Used for authenticated endpoints."""
    login_url = f"{base_url}/login"
    response = requests.post(login_url, json=user_credentials)
    assert response.status_code == 200, f"Login failed with status {response.status_code}"
    data = response.json()
    token = data.get("access_token") or data.get("token")
    assert token, "JWT token not found in login response"
    return token


@pytest.fixture
def auth_headers(auth_token):
    """Headers with Authorization Bearer token and JSON content type."""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }


@pytest.fixture
def client():
    """A requests.Session for the duration of a test (e.g. for cookies)."""
    with requests.Session() as session:
        yield session
