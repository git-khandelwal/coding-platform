"""Shared fixtures for UI tests."""
import os
import pytest


@pytest.fixture(scope="session")
def base_url():
    return os.getenv("API_BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def user_credentials():
    return {
        "username": os.getenv("TEST_USERNAME", "testuser"),
        "password": os.getenv("TEST_PASSWORD", "testpass"),
    }
