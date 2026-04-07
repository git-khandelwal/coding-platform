import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from playwright.sync_api import sync_playwright

# --- Selenium Page Objects ---

class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    def login(self, username, password):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-form"))
        )
        self.driver.find_element(By.ID, "login-username").send_keys(username)
        self.driver.find_element(By.ID, "login-password").send_keys(password)
        self.driver.find_element(By.ID, "login-form").submit()

class EditProblemPage:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_load(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "problemForm"))
        )

    def get_field_value(self, field_id):
        elem = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, field_id))
        )
        if elem.tag_name == "input":
            return elem.get_attribute("value")
        elif elem.tag_name == "textarea":
            return elem.get_attribute("value")
        else:
            return elem.text

# --- Playwright Page Objects ---

class PWLoginPage:
    def __init__(self, page):
        self.page = page

    def login(self, username, password):
        self.page.wait_for_selector("#login-form")
        self.page.fill("#login-username", username)
        self.page.fill("#login-password", password)
        self.page.click("#login-form button[type='submit']")

class PWEditProblemPage:
    def __init__(self, page):
        self.page = page

    def wait_for_load(self):
        self.page.wait_for_selector("#problemForm")

    def get_field_value(self, field_id):
        elem = self.page.wait_for_selector(f"#{field_id}")
        tag = elem.evaluate("el => el.tagName.toLowerCase()")
        if tag == "input" or tag == "textarea":
            return elem.input_value()
        else:
            return elem.text_content()

# --- Fixtures ---

@pytest.fixture(scope="function")
def selenium_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def playwright_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()

# --- Test Data ---

TEST_USER = "testuser"
TEST_PASS = "testpass"
PROBLEM_ID = 1  # Assumes a problem with ID 1 exists for testing
EXPECTED_PROBLEM_DATA = {
    "title": "Sample Problem Title",
    "description": "Sample problem description.",
    "difficulty": "Easy",
    "input_format": "Input format details.",
    "output_format": "Output format details.",
    "sample_input": "Sample input",
    "sample_output": "Sample output",
    "sample_code": "print('Hello World')",
    "constraints": "Constraints details."
}

# --- Selenium Test ---

def test_tc005_edit_problem_ui_authenticated_selenium(selenium_driver):
    driver = selenium_driver
    driver.get("http://localhost:5000/")
    login_page = LoginPage(driver)
    login_page.login(TEST_USER, TEST_PASS)

    # Navigate to edit problem page
    edit_url = f"http://localhost:5000/problems/{PROBLEM_ID}/edit"
    driver.get(edit_url)
    edit_page = EditProblemPage(driver)
    edit_page.wait_for_load()

    # Assert all fields are pre-filled with expected data
    for field, expected in EXPECTED_PROBLEM_DATA.items():
        actual = edit_page.get_field_value(field)
        assert actual == expected, f"Field '{field}' expected '{expected}' but got '{actual}'"

# --- Playwright Test ---

def test_tc005_edit_problem_ui_authenticated_playwright(playwright_page):
    page = playwright_page
    page.goto("http://localhost:5000/")
    login_page = PWLoginPage(page)
    login_page.login(TEST_USER, TEST_PASS)

    # Navigate to edit problem page
    edit_url = f"http://localhost:5000/problems/{PROBLEM_ID}/edit"
    page.goto(edit_url)
    edit_page = PWEditProblemPage(page)
    edit_page.wait_for_load()

    # Assert all fields are pre-filled with expected data
    for field, expected in EXPECTED_PROBLEM_DATA.items():
        actual = edit_page.get_field_value(field)
        assert actual == expected, f"Field '{field}' expected '{expected}' but got '{actual}'"