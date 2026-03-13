import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from playwright.sync_api import sync_playwright

# --- Selenium Page Object ---
class ProblemsListPageSelenium:
    def __init__(self, driver):
        self.driver = driver

    def wait_until_loaded(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "problemsList"))
        )

    def get_problem_items(self):
        self.wait_until_loaded()
        return self.driver.find_elements(By.CSS_SELECTOR, "#problemsList > li")

    def get_problem_title_and_difficulty(self, li_elem):
        # Assuming structure: <li> <a class="problem-link">Title</a> <span class="difficulty">Difficulty</span> </li>
        title_elem = li_elem.find_element(By.CSS_SELECTOR, ".problem-link")
        difficulty_elem = li_elem.find_element(By.CSS_SELECTOR, ".difficulty")
        return title_elem.text, difficulty_elem.text

# --- Playwright Page Object ---
class ProblemsListPagePlaywright:
    def __init__(self, page):
        self.page = page

    def wait_until_loaded(self):
        self.page.wait_for_selector("#problemsList")

    def get_problem_items(self):
        self.wait_until_loaded()
        return self.page.query_selector_all("#problemsList > li")

    def get_problem_title_and_difficulty(self, li_elem):
        title_elem = li_elem.query_selector(".problem-link")
        difficulty_elem = li_elem.query_selector(".difficulty")
        return title_elem.inner_text(), difficulty_elem.inner_text()

# --- Selenium Fixtures ---
@pytest.fixture(scope="function")
def selenium_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

# --- Playwright Fixtures ---
@pytest.fixture(scope="function")
def playwright_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()

# --- Selenium Test ---
def test_tc001_problems_list_ui_selenium(selenium_driver):
    selenium_driver.get("http://localhost:5000/problems")
    page = ProblemsListPageSelenium(selenium_driver)
    page.wait_until_loaded()
    problem_items = page.get_problem_items()
    assert len(problem_items) > 0, "No problems found in the list."

    for li_elem in problem_items:
        title, difficulty = page.get_problem_title_and_difficulty(li_elem)
        assert title.strip() != "", "Problem title is missing."
        assert difficulty.strip() != "", "Problem difficulty is missing."
        # Optionally: check difficulty is one of expected values
        assert difficulty in ["Easy", "Medium", "Hard"], f"Unexpected difficulty: {difficulty}"

# --- Playwright Test ---
def test_tc001_problems_list_ui_playwright(playwright_page):
    playwright_page.goto("http://localhost:5000/problems")
    page = ProblemsListPagePlaywright(playwright_page)
    page.wait_until_loaded()
    problem_items = page.get_problem_items()
    assert len(problem_items) > 0, "No problems found in the list."

    for li_elem in problem_items:
        title, difficulty = page.get_problem_title_and_difficulty(li_elem)
        assert title.strip() != "", "Problem title is missing."
        assert difficulty.strip() != "", "Problem difficulty is missing."
        assert difficulty in ["Easy", "Medium", "Hard"], f"Unexpected difficulty: {difficulty}"