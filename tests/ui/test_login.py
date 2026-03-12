"""UI test: login flow on the home page."""
import pytest
from playwright.sync_api import Page, expect


def test_login_success(page: Page, base_url: str, user_credentials: dict):
    """Submit login form and verify successful login (token stored, protected content works)."""
    page.goto(base_url)

    # Accept alert dialog when login succeeds
    page.on("dialog", lambda d: d.accept())

    page.locator("#login-username").fill(user_credentials["username"])
    page.locator("#login-password").fill(user_credentials["password"])
    page.locator("#login-form").get_by_role("button", name="Login").click()

    # Wait a moment for the request and localStorage to update
    page.wait_for_timeout(500)

    # Token should be in localStorage after successful login
    token = page.evaluate("() => localStorage.getItem('token')")
    assert token is not None and len(token) > 0, "Expected JWT token in localStorage after login"

    # Verify protected content: click "Get Protected Content" and check greeting
    page.get_by_role("button", name="Get Protected Content").click()
    content = page.locator("#protected-content")
    content.wait_for(state="visible", timeout=5000)
    expect(content).to_contain_text(user_credentials["username"])
