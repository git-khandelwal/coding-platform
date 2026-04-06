"""UI test: login flow on the home page."""
import pytest
from playwright.sync_api import Page, expect

from tests.lib.ui import login_and_get_token


def test_login_success(page: Page, base_url: str, user_credentials: dict):
    """Submit login form and verify successful login (token stored, protected content works)."""
    token = login_and_get_token(page, base_url, user_credentials)

    # Verify protected content: click "Get Protected Content" and check greeting
    page.get_by_role("button", name="Get Protected Content").click()
    content = page.locator("#protected-content")
    content.wait_for(state="visible", timeout=5000)
    expect(content).to_contain_text(user_credentials["username"])
