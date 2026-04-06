"""Shared fixtures for UI tests."""
import pytest

from tests.lib.config import get_base_url, get_user_credentials


@pytest.fixture(scope="session")
def base_url():
    return get_base_url()


@pytest.fixture(scope="session")
def user_credentials():
    return get_user_credentials()
