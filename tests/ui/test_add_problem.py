"""UI test: add new problem flow (requires login)."""
import pytest
from playwright.sync_api import Page, expect


def test_add_problem_success(page: Page, base_url: str, user_credentials: dict):
    """Log in, go to Add Problem, submit form and verify success or redirect."""
    page.goto(base_url)

    # Accept alerts (login success and add problem success)
    page.on("dialog", lambda d: d.accept())

    # Login first (add problem page requires JWT)
    page.locator("#login-username").fill(user_credentials["username"])
    page.locator("#login-password").fill(user_credentials["password"])
    page.locator("#login-form").get_by_role("button", name="Login").click()
    page.wait_for_timeout(500)

    token = page.evaluate("() => localStorage.getItem('token')")
    assert token, "Login failed; no token in localStorage"

    # Go to Add Problem page
    page.goto(f"{base_url}/problems/add")
    page.wait_for_load_state("networkidle")

    # Fill the add-problem form
    page.locator("#title").fill("UI Test Problem")
    page.locator("#description").fill("Description for UI test.")
    page.locator("#difficulty").fill("Easy")
    page.locator("#input_format").fill("One line of input.")
    page.locator("#output_format").fill("One line of output.")
    page.locator("#sample_input").fill("1")
    page.locator("#sample_output").fill("2")
    page.locator("#sample_code").fill("")
    page.locator("#constraints").fill("1 <= n <= 100")

    # Submit form
    page.locator("#problemForm").get_by_role("button", name="Add Problem").click()

    # Success: redirect to problems list (not /problems/add)
    page.wait_for_url(f"{base_url}/problems", timeout=10000)
    expect(page).to_have_url(f"{base_url}/problems")
