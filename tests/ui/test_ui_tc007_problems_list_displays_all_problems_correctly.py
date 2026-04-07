import pytest
from playwright.sync_api import sync_playwright, Page, expect
from typing import List, Tuple

# ------------------------------------------------------------------
# Page Object Model
# ------------------------------------------------------------------
class ProblemsPage:
    """Page object for the Problems List page."""

    URL = "/problems"

    def __init__(self, page: Page):
        self.page = page

    def navigate(self):
        """Navigate to the problems list page."""
        self.page.goto(self.URL)
        # Wait for the table to be visible
        self.page.wait_for_selector("table.problems-table tbody tr", state="visible")

    def get_problem_rows(self) -> List[Page]:
        """Return a list of row elements representing each problem."""
        return self.page.query_selector_all("table.problems-table tbody tr")

    def get_problem_data(self, row: Page) -> Tuple[str, str, str]:
        """
        Extract problem title, difficulty, and ID from a row.
        Returns:
            title (str), difficulty (str), id (str)
        """
        title_el = row.query_selector("td a.problem-link")
        difficulty_el = row.query_selector("td span.problem-difficulty")
        # The ID is embedded in the href of the link
        href = title_el.get_attribute("href")
        problem_id = href.split("/")[-1] if href else ""
        title = title_el.inner_text().strip()
        difficulty = difficulty_el.inner_text().strip()
        return title, difficulty, problem_id

    def get_difficulty_color(self, difficulty_el: Page) -> str:
        """Return the computed background color of the difficulty element."""
        return difficulty_el.evaluate("el => getComputedStyle(el).backgroundColor")

# ------------------------------------------------------------------
# Test Fixtures
# ------------------------------------------------------------------
@pytest.fixture(scope="session")
def playwright_context():
    """Launch Playwright browser and provide a context."""
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

# ------------------------------------------------------------------
# Test Case: TC007
# ------------------------------------------------------------------
def test_tc007_problems_list_displays_all_problems_correctly(page: Page):
    """
    Verify that the problems list page shows all problems with correct titles,
    difficulty labels, and color coding.
    """
    problems_page = ProblemsPage(page)
    problems_page.navigate()

    rows = problems_page.get_problem_rows()
    assert rows, "No problem rows found on the page."

    # Expected difficulty to background color mapping (RGB)
    difficulty_color_map = {
        "Easy": "rgb(212, 237, 218)",   # #d4edda
        "Medium": "rgb(255, 243, 205)", # #fff3cd
        "Hard": "rgb(248, 215, 218)",   # #f8d7da
    }

    for idx, row in enumerate(rows, start=1):
        title, difficulty, problem_id = problems_page.get_problem_data(row)

        # 1. Each card displays the problem title, difficulty, and ID.
        assert title, f"Row {idx}: Title is empty."
        assert difficulty in difficulty_color_map, f"Row {idx}: Unexpected difficulty '{difficulty}'."
        assert problem_id, f"Row {idx}: Problem ID is missing."

        # 2. Difficulty labels use the correct color coding.
        difficulty_el = row.query_selector("td span.problem-difficulty")
        actual_color = problems_page.get_difficulty_color(difficulty_el)
        expected_color = difficulty_color_map[difficulty]
        assert actual_color == expected_color, (
            f"Row {idx}: Difficulty '{difficulty}' has color '{actual_color}', "
            f"expected '{expected_color}'."
        )
        # Optional: log success for each row
        print(f"Row {idx}: '{title}' (ID: {problem_id}) - Difficulty: {difficulty} - Color OK")

# ------------------------------------------------------------------
# End of test file
# ------------------------------------------------------------------