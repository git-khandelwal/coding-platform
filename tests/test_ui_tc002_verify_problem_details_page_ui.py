import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from playwright.sync_api import sync_playwright

# --- Selenium Page Objects ---

class ProblemsListPage:
    def __init__(self, driver):
        self.driver = driver

    def open(self, base_url):
        self.driver.get(f"{base_url}/problems")

    def click_first_problem(self):
        # Assuming problems are listed as links or buttons with a unique selector
        # We'll use the first link/button that navigates to /problems/<id>
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/problems/')]"))
        )
        first_problem_link = self.driver.find_element(By.XPATH, "//a[contains(@href, '/problems/')]")
        first_problem_link.click()


class ProblemDetailsPage:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_load(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "description"))
        )

    def get_title(self):
        return self.driver.find_element(By.ID, "title").text

    def get_description(self):
        return self.driver.find_element(By.ID, "description").text

    def get_input_format(self):
        return self.driver.find_element(By.ID, "input_format").text

    def get_output_format(self):
        return self.driver.find_element(By.ID, "output_format").text

    def get_sample_input(self):
        return self.driver.find_element(By.ID, "sample_input").text

    def get_sample_output(self):
        return self.driver.find_element(By.ID, "sample_output").text

    def get_constraints(self):
        return self.driver.find_element(By.ID, "constraints").text

# --- Selenium Fixtures ---

@pytest.fixture(scope="function")
def selenium_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

# --- Playwright Fixtures ---

@pytest.fixture(scope="function")
def playwright_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

# --- Selenium Test ---

def test_tc002_problem_details_ui_selenium(selenium_driver):
    base_url = "http://localhost:5000"
    problems_page = ProblemsListPage(selenium_driver)
    problems_page.open(base_url)
    problems_page.click_first_problem()

    details_page = ProblemDetailsPage(selenium_driver)
    details_page.wait_for_load()

    # Assert all required fields are present and non-empty
    assert details_page.get_title(), "Problem title not displayed"
    assert details_page.get_description(), "Problem description not displayed"
    assert details_page.get_input_format(), "Input format not displayed"
    assert details_page.get_output_format(), "Output format not displayed"
    assert details_page.get_sample_input(), "Sample input not displayed"
    assert details_page.get_sample_output(), "Sample output not displayed"
    assert details_page.get_constraints(), "Constraints not displayed"

# --- Playwright Test ---

def test_tc002_problem_details_ui_playwright(playwright_browser):
    base_url = "http://localhost:5000"
    context = playwright_browser.new_context()
    page = context.new_page()

    # Navigate to problems list
    page.goto(f"{base_url}/problems")
    page.wait_for_load_state("domcontentloaded")

    # Click the first problem link (assume it's an <a> with href containing /problems/)
    page.wait_for_selector("a[href^='/problems/']")
    first_problem_link = page.query_selector("a[href^='/problems/']")
    assert first_problem_link is not None, "No problem link found"
    first_problem_link.click()

    # Wait for problem details page to load
    page.wait_for_selector("#description")

    # Assert all required fields are present and non-empty
    assert page.query_selector("#title") is not None, "Problem title not displayed"
    assert page.query_selector("#description") is not None, "Problem description not displayed"
    assert page.query_selector("#input_format") is not None, "Input format not displayed"
    assert page.query_selector("#output_format") is not None, "Output format not displayed"
    assert page.query_selector("#sample_input") is not None, "Sample input not displayed"
    assert page.query_selector("#sample_output") is not None, "Sample output not displayed"
    assert page.query_selector("#constraints") is not None, "Constraints not displayed"

    # Optionally, check that the fields are not empty
    assert page.query_selector("#title").inner_text().strip(), "Problem title is empty"
    assert page.query_selector("#description").inner_text().strip(), "Problem description is empty"
    assert page.query_selector("#input_format").inner_text().strip(), "Input format is empty"
    assert page.query_selector("#output_format").inner_text().strip(), "Output format is empty"
    assert page.query_selector("#sample_input").inner_text().strip(), "Sample input is empty"
    assert page.query_selector("#sample_output").inner_text().strip(), "Sample output is empty"
    assert page.query_selector("#constraints").inner_text().strip(), "Constraints are empty"

    context.close()