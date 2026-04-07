import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from playwright.sync_api import sync_playwright

# --- Selenium Page Object ---
class ProblemDetailsPageSelenium:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_constraints_section(self, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.ID, "constraints"))
        )

    def get_constraints_text(self):
        constraints_elem = self.wait_for_constraints_section()
        return constraints_elem.text

# --- Playwright Page Object ---
class ProblemDetailsPagePlaywright:
    def __init__(self, page):
        self.page = page

    def wait_for_constraints_section(self, timeout=10000):
        return self.page.wait_for_selector("#constraints", state="visible", timeout=timeout)

    def get_constraints_text(self):
        self.wait_for_constraints_section()
        return self.page.locator("#constraints").inner_text()

# --- Selenium Fixtures ---
@pytest.fixture(scope="function")
def selenium_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    service = ChromeService()
    driver = webdriver.Chrome(service=service, options=options)
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

# --- Test Data ---
@pytest.fixture(scope="function")
def problem_details_url():
    # Replace with a valid problem ID for your environment
    return "http://localhost:5000/problems/1"

# --- Selenium Test ---
def test_tc016_constraints_section_formatting_selenium(selenium_driver, problem_details_url):
    selenium_driver.get(problem_details_url)
    page = ProblemDetailsPageSelenium(selenium_driver)
    constraints_text = page.get_constraints_text()
    assert constraints_text.strip() != "", "Constraints section should not be empty"
    # Optionally check formatting: e.g., multiline, bullet points, etc.
    assert len(constraints_text.splitlines()) >= 1, "Constraints section should be clearly formatted"

# --- Playwright Test ---
def test_tc016_constraints_section_formatting_playwright(playwright_page, problem_details_url):
    playwright_page.goto(problem_details_url)
    page = ProblemDetailsPagePlaywright(playwright_page)
    constraints_text = page.get_constraints_text()
    assert constraints_text.strip() != "", "Constraints section should not be empty"
    assert len(constraints_text.splitlines()) >= 1, "Constraints section should be clearly formatted"