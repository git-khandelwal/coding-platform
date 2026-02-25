import os
import pytest
from playwright.sync_api import sync_playwright, Page, expect

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
USERNAME = os.getenv("TEST_USER", "fortnite")
PASSWORD = os.getenv("TEST_PASS", "fortnite")


class ProblemsListPage:
    def __init__(self, page: Page):
        self.page = page
        self.card_selector = ".problem-card"  # adjust based on actual markup

    def navigate(self):
        self.page.goto(f"{BASE_URL}/problems")

    def click_first_problem(self):
        self.page.wait_for_selector(self.card_selector, state="visible")
        self.page.click(f"{self.card_selector}:nth-child(1)")


class ProblemDetailsPage:
    def __init__(self, page: Page):
        self.page = page
        self.title_selector = ".problem-title"
        self.description_selector = ".problem-description"
        self.difficulty_selector = ".problem-difficulty"
        self.input_format_selector = ".problem-input-format"
        self.output_format_selector = ".problem-output-format"
        self.sample_input_selector = ".problem-sample-input"
        self.sample_output_selector = ".problem-sample-output"
        self.constraints_selector = ".problem-constraints"
        self.sample_code_selector = ".problem-sample-code"
        self.solve_button_selector = "button#solve-button"

    def wait_for_elements(self):
        selectors = [
            self.title_selector,
            self.description_selector,
            self.difficulty_selector,
            self.input_format_selector,
            self.output_format_selector,
            self.sample_input_selector,
            self.sample_output_selector,
            self.constraints_selector,
            self.sample_code_selector,
            self.solve_button_selector,
        ]
        for sel in selectors:
            self.page.wait_for_selector(sel, state="visible")

    def verify_fields_present(self):
        expect(self.page.locator(self.title_selector)).to_be_visible()
        expect(self.page.locator(self.description_selector)).to_be_visible()
        expect(self.page.locator(self.difficulty_selector)).to_be_visible()
        expect(self.page.locator(self.input_format_selector)).to_be_visible()
        expect(self.page.locator(self.output_format_selector)).to_be_visible()
        expect(self.page.locator(self.sample_input_selector)).to_be_visible()
        expect(self.page.locator(self.sample_output_selector)).to_be_visible()
        expect(self.page.locator(self.constraints_selector)).to_be_visible()
        expect(self.page.locator(self.sample_code_selector)).to_be_visible()

    def verify_solve_button(self):
        solve_btn = self.page.locator(self.solve_button_selector)
        expect(solve_btn).to_be_visible()
        expect(solve_btn).to_be_enabled()


@pytest.fixture(scope="session")
def playwright_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        yield context
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def page(playwright_context):
    page = playwright_context.new_page()
    yield page
    page.close()


def login(page: Page):
    page.goto(f"{BASE_URL}/")
    page.wait_for_selector("#login-username", state="visible")
    page.fill("#login-username", USERNAME)
    page.fill("#login-password", PASSWORD)
    page.click("button[type='submit']")
    # Wait for login to complete, e.g., by checking presence of protected content or redirect
    page.wait_for_selector("#protected-content", state="visible", timeout=5000)


def test_tc007_problem_details_page_content(page: Page):
    """
    TC007: Problem details page content
    Verify that the details page shows full problem information and a solve button.
    """
    try:
        # Ensure user is logged in
        login(page)

        # Navigate to problems list
        problems_page = ProblemsListPage(page)
        problems_page.navigate()

        # Click the first problem card
        problems_page.click_first_problem()

        # Verify details page
        details_page = ProblemDetailsPage(page)
        details_page.wait_for_elements()
        details_page.verify_fields_present()
        details_page.verify_solve_button()

    except Exception as e:
        pytest.fail(f"Test failed due to exception: {e}")