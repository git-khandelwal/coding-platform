import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ----------------------------------------------------------------------
# Page Objects
# ----------------------------------------------------------------------
class ProblemsListPage:
    """Page object for the /problems page."""

    URL = "/problems"

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(self.driver, 10)

    def load(self):
        """Navigate to the problems list page."""
        self.driver.get(f"{self.base_url}{self.URL}")
        # Wait for the list container to be present
        self.wait.until(EC.presence_of_element_located((By.ID, "problemsList")))

    def get_problem_cards(self):
        """Return a list of WebElement objects representing problem cards."""
        return self.driver.find_elements(By.CSS_SELECTOR, "ul#problemsList li")

    def get_problem_details(self, card):
        """
        Extract title, difficulty, and ID from a problem card element.
        Assumes the card contains an <a> with class 'problem-link' and a data-id attribute.
        """
        link = card.find_element(By.CSS_SELECTOR, "a.problem-link")
        title = link.text.strip()
        # Difficulty is displayed in a span with class 'problem-difficulty'
        difficulty_span = card.find_element(By.CSS_SELECTOR, "span.problem-difficulty")
        difficulty = difficulty_span.text.strip()
        # ID is stored in a data attribute on the <a>
        problem_id = link.get_attribute("data-id")
        return {"title": title, "difficulty": difficulty, "id": problem_id}

    def click_card(self, card):
        """Click on the problem card to navigate to the details page."""
        link = card.find_element(By.CSS_SELECTOR, "a.problem-link")
        link.click()
        # Wait for navigation to complete by checking URL change
        self.wait.until(EC.url_contains("/problems/"))


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------
@pytest.fixture(scope="session")
def base_url():
    """
    Base URL of the application under test.
    Adjust the host and port if the test environment differs.
    """
    return os.getenv("APP_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def driver():
    """Set up Selenium WebDriver (Chrome) for the test session."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run headless for CI environments
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    yield driver
    driver.quit()


@pytest.fixture
def problems_page(driver, base_url):
    """Instantiate the ProblemsListPage and load it."""
    page = ProblemsListPage(driver, base_url)
    page.load()
    return page


# ----------------------------------------------------------------------
# Test Case: TC006 - Problems list displays all problems
# ----------------------------------------------------------------------
def test_problems_list_displays_all_problems(problems_page):
    """
    Verify that the /problems page lists every problem with title, difficulty, and ID,
    and that each card is clickable and navigates to the problem details page.
    """
    cards = problems_page.get_problem_cards()
    assert cards, "No problem cards found on the /problems page."

    for idx, card in enumerate(cards, start=1):
        details = problems_page.get_problem_details(card)
        # Verify title is non-empty
        assert details["title"], f"Card {idx} missing title."
        # Verify difficulty is one of the expected values
        assert details["difficulty"].lower() in {"easy", "medium", "hard"}, (
            f"Card {idx} has unexpected difficulty: {details['difficulty']}"
        )
        # Verify ID is present and numeric
        assert details["id"], f"Card {idx} missing ID."
        assert details["id"].isdigit(), f"Card {idx} has non-numeric ID: {details['id']}"

    # Click the first card and verify navigation
    first_card = cards[0]
    problems_page.click_card(first_card)

    # Wait for the details page to load and verify URL contains the problem ID
    problem_id = problems_page.get_problem_details(first_card)["id"]
    WebDriverWait(problems_page.driver, 10).until(
        EC.url_contains(f"/problems/{problem_id}")
    )
    # Optionally, verify that the details page contains the title
    title_element = problems_page.driver.find_element(By.TAG_NAME, "h1")
    assert title_element.text.strip() == problems_page.get_problem_details(first_card)["title"], (
        "Problem details page title does not match the clicked card title."
    )