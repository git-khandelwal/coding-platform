import json
import time

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


BASE_URL = "http://localhost:5000"


class LoginPage:
    """Page object for the login page."""

    def __init__(self, driver):
        self.driver = driver
        self.username_input = (By.ID, "login-username")
        self.password_input = (By.ID, "login-password")
        self.login_button = (By.XPATH, "//button[text()='Login']")

    def login(self, username: str, password: str):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.username_input)
        )
        self.driver.find_element(*self.username_input).clear()
        self.driver.find_element(*self.username_input).send_keys(username)
        self.driver.find_element(*self.password_input).clear()
        self.driver.find_element(*self.password_input).send_keys(password)
        self.driver.find_element(*self.login_button).click()


class ProblemsPage:
    """Page object for the problems list page."""

    def __init__(self, driver):
        self.driver = driver

    def navigate_to_problem(self, problem_id: int):
        url = f"{BASE_URL}/problems/{problem_id}/solve"
        self.driver.get(url)
        # Wait for the solve page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )


class SolvePage:
    """Page object for the problem solve page."""

    def __init__(self, driver):
        self.driver = driver
        self.code_editor = (By.CSS_SELECTOR, "textarea")  # adjust if needed
        self.submit_button = (By.XPATH, "//button[text()='Submit']")
        self.message = (By.CSS_SELECTOR, ".alert")  # adjust if needed
        self.status = (By.CSS_SELECTOR, "#status")  # adjust if needed
        self.result = (By.CSS_SELECTOR, "#result")  # adjust if needed

    def write_code(self, code: str):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.code_editor)
        )
        editor = self.driver.find_element(*self.code_editor)
        editor.clear()
        editor.send_keys(code)

    def submit(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.submit_button)
        )
        self.driver.find_element(*self.submit_button).click()

    def get_message_text(self) -> str:
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.message)
            )
            return element.text.strip()
        except TimeoutException:
            return ""

    def get_status_text(self) -> str:
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.status)
            )
            return element.text.strip()
        except TimeoutException:
            return ""

    def get_result_text(self) -> str:
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.result)
            )
            return element.text.strip()
        except TimeoutException:
            return ""


@pytest.fixture(scope="session")
def driver():
    """Setup Selenium WebDriver."""
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)
    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def login(driver):
    """Login fixture to ensure user is authenticated."""
    login_page = LoginPage(driver)
    driver.get(BASE_URL)
    # Assuming a test user exists; replace with actual credentials
    login_page.login("testuser", "testpass")
    # Wait for login to complete, e.g., by checking presence of a logout button
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "logout-button"))
        )
    except TimeoutException:
        pytest.fail("Login failed: logout button not found.")


def test_submitting_correct_code_shows_success_status(driver, login):
    """
    TC010: Submitting correct code shows success status.
    """
    problem_id = 1  # Assumes problem with ID 1 exists
    problems_page = ProblemsPage(driver)
    problems_page.navigate_to_problem(problem_id)

    solve_page = SolvePage(driver)

    # Sample correct solution (adjust based on actual problem)
    correct_code = """
def solve(a, b):
    return a + b
"""

    solve_page.write_code(correct_code)
    solve_page.submit()

    # Verify the expected results
    assert (
        "Submission evaluated" in solve_page.get_message_text()
    ), "Expected 'Submission evaluated' message not found."

    assert (
        solve_page.get_status_text() == "Success"
    ), f"Expected status 'Success', got '{solve_page.get_status_text()}'"

    assert (
        solve_page.get_result_text() == "Correct"
    ), f"Expected result 'Correct', got '{solve_page.get_result_text()}'"

    # Ensure no error messages are displayed
    error_elements = driver.find_elements(By.CSS_SELECTOR, ".error")
    assert len(error_elements) == 0, "Unexpected error messages found."