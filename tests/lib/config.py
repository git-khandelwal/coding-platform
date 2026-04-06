import os


def get_base_url() -> str:
    """Base URL for app/API under test."""
    return os.getenv("API_BASE_URL", os.getenv("BASE_URL", "http://localhost:5000"))


def get_user_credentials() -> dict:
    """Valid user credentials for login."""
    return {
        "username": os.getenv("TEST_USERNAME", "testuser"),
        "password": os.getenv("TEST_PASSWORD", "testpass"),
    }

