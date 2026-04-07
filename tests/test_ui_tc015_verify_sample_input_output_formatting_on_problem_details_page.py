import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from playwright.sync_api import sync_playwright

# --- Selenium Page Object ---
class ProblemDetailsPageSelenium:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_sample_sections(self):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "sample_input"))
        )
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "sample_output"))
        )

    def get_sample_input(self):
        return self.driver.find_element(By.ID, "sample_input").text

    def get_sample_output(self):
        return self.driver.find_element(By.ID, "sample_output").text

# --- Playwright Page Object ---
class ProblemDetailsPagePlaywright:
    def __init__(self, page):
        self.page = page

    def wait_for_sample_sections(self):
        self.page.wait_for_selector("#sample_input", state="visible", timeout=10000)
        self.page.wait_for_selector("#sample_output", state="visible", timeout=10000)

    def get_sample_input(self):
        return self.page.locator("#sample_input").inner_text()

    def get_sample_output(self):
        return self.page.locator("#sample_output").inner_text()

# --- Fixtures ---
@pytest.fixture(scope="function")
def selenium_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def playwright_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        yield page
        context.close()
        browser.close()

# --- Test Data ---
PROBLEM_DETAILS_URL = "http://localhost:5000/problems/1"  # Adjust as needed

# --- Selenium Test ---
def test_tc015_sample_io_formatting_selenium(selenium_driver):
    selenium_driver.get(PROBLEM_DETAILS_URL)
    page = ProblemDetailsPageSelenium(selenium_driver)
    page.wait_for_sample_sections()

    sample_input = page.get_sample_input()
    sample_output = page.get_sample_output()

    assert sample_input.strip() != "", "Sample input should not be empty"
    assert sample_output.strip() != "", "Sample output should not be empty"
    # Check formatting: multiline or code-like
    assert "\n" in sample_input or len(sample_input) > 10, "Sample input should be formatted/readable"
    assert "\n" in sample_output or len(sample_output) > 10, "Sample output should be formatted/readable"

# --- Playwright Test ---
def test_tc015_sample_io_formatting_playwright(playwright_context):
    page = playwright_context
    page.goto(PROBLEM_DETAILS_URL)
    details_page = ProblemDetailsPagePlaywright(page)
    details_page.wait_for_sample_sections()

    sample_input = details_page.get_sample_input()
    sample_output = details_page.get_sample_output()

    assert sample_input.strip() != "", "Sample input should not be empty"
    assert sample_output.strip() != "", "Sample output should not be empty"
    assert "\n" in sample_input or len(sample_input) > 10, "Sample input should be formatted/readable"
    assert "\n" in sample_output or len(sample_output) > 10, "Sample output should be formatted/readable"