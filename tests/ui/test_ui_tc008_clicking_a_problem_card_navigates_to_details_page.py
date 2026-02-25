import re
import pytest
from playwright.sync_api import sync_playwright, Page, expect

BASE_URL = "http://localhost:5000"


class ProblemsListPage:
    """Page object for the problems list page."""

    def __init__(self, page: Page):
        self.page = page
        self.url = f"{BASE_URL}/problems"
        self.problem_cards_selector = "ul#problemsList li"

    def open(self):
        """Navigate to the problems list page."""
        self.page.goto(self.url)
        self.page.wait_for_selector(self.problem_cards_selector)

    def get_first_problem_card(self):
        """Return the locator for the first problem card."""
        return self.page.locator(self.problem_cards_selector).first

    def click_first_problem_card(self):
        """Click the first problem card and return its ID."""
        card = self.get_first_problem_card()
        # Extract problem ID from data attribute or href if present
        href = card.get_attribute("href") or card.get_attribute("data-href")
        problem_id = None
        if href:
            match = re.search(r"/problems/(\d+)", href)
            if match:
                problem_id = int(match.group(1))
        card.click()
        return problem_id


class ProblemDetailsPage:
    """Page object for the problem details page."""

    def __init__(self, page: Page):
        self.page = page
        self.title_selector = "h1.problem-title"
        self.id_selector = "span.problem-id"

    def wait_for_load(self):
        """Wait until the problem details are loaded."""
        self.page.wait_for_selector(self.title_selector)

    def get_title(self) -> str:
        """Return the problem title."""
        return self.page.locator(self.title_selector).inner_text()

    def get_id(self) -> int:
        """Return the problem ID."""
        id_text = self.page.locator(self.id_selector).inner_text()
        return int(id_text)


@pytest.fixture(scope="session")
def playwright_context():
    """Set up Playwright browser context."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        yield context
        context.close()
        browser.close()


@pytest.fixture
def page(playwright_context) -> Page:
    """Create a new page for each test."""
    page = playwright_context.new_page()
    yield page
    page.close()


def test_click_problem_card_navigates_to_details(page: Page):
    """
    TC008: Clicking a problem card navigates to details page.
    """
    # Arrange
    problems_page = ProblemsListPage(page)
    problems_page.open()

    # Act
    problem_id = problems_page.click_first_problem_card()

    # Assert navigation
    expect(page).to_have_url(re.compile(rf"/problems/{problem_id}"))

    # Verify details page content
    details_page = ProblemDetailsPage(page)
    details_page.wait_for_load()
    assert details_page.get_id() == problem_id, "Problem ID on details page does not match clicked card"
    assert details_page.get_title(), "Problem title should be displayed on details page"
    # Additional checks can be added here (description, difficulty, etc.) if selectors are known
    # Example:
    # assert page.locator("div.problem-description").inner_text(), "Description should be present"

    # Clean up: navigate back to list (optional)
    page.go_back()
    expect(page).to_have_url(re.compile(r"/problems$"))
    page.wait_for_selector(problems_page.problem_cards_selector)
    # Test ends here; teardown handled by fixtures