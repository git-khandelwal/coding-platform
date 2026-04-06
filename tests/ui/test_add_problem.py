"""UI test: add new problem flow (requires login)."""
import pytest
from playwright.sync_api import Page, expect

from tests.lib.ui import goto_add_problem, login_and_get_token


def test_add_problem_success(page: Page, base_url: str, user_credentials: dict):
    """Log in, go to Add Problem, submit form and verify success or redirect."""
    login_and_get_token(page, base_url, user_credentials)
    goto_add_problem(page, base_url)

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
