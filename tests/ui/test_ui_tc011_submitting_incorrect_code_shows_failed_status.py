import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Configuration (replace with actual values or environment variables)
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
USERNAME = os.getenv("TEST_USERNAME", "testuser")
PASSWORD = os.getenv("TEST_PASSWORD", "testpass")
PROBLEM_ID = os.getenv("TEST_PROBLEM_ID", "1")  # ID of an existing problem

# Page Object Models
class BasePage:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def wait_for_element(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        element = self.wait_for_element(locator)
        element.click()

    def send_keys(self, locator, text):
        element = self.wait_for_element(locator)
        element.clear()
        element.send_keys(text)

class LoginPage(BasePage):
    USERNAME_INPUT = (By.ID, "login-username")
    PASSWORD_INPUT = (By.ID, "login-password")
    LOGIN_BUTTON = (By.XPATH, "//form[@id='login-form']//button[@type='submit']")

    def login(self, username: str, password: str):
        self.send_keys(self.USERNAME_INPUT, username)
        self.send_keys(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

class ProblemSolvePage(BasePage):
    CODE_EDITOR = (By.ID, "code-editor")  # Assumed ID for the code editor textarea
    SUBMIT_BUTTON = (By.ID, "submit-btn")  # Assumed ID for the submit button
    MESSAGE = (By.ID, "submission-message")  # Assumed ID for the message element
    STATUS = (By.ID, "submission-status")  # Assumed ID for the status element
    RESULT = (By.ID, "submission-result")  # Assumed ID for the result element

    def write_code(self, code: str):
        self.send_keys(self.CODE_EDITOR, code)

    def submit(self):
        self.click(self.SUBMIT_BUTTON)

    def get_message(self) -> str:
        element = self.wait_for_element(self.MESSAGE)
        return element.text.strip()

    def get_status(self) -> str:
        element = self.wait_for_element(self.STATUS)
        return element.text.strip()

    def get_result(self) -> str:
        element = self.wait_for_element(self.RESULT)
        return element.text.strip()

# Fixtures
@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    yield driver
    driver.quit()

@pytest.fixture(scope="session")
def login(driver):
    driver.get(f"{BASE_URL}/")
    login_page = LoginPage(driver)
    login_page.login(USERNAME, PASSWORD)
    # Wait for login to complete, e.g., by checking presence of a logout button or user profile
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "logout-button"))
        )
    except TimeoutException:
        pytest.fail("Login failed: Logout button not found.")
    return driver

@pytest.fixture
def problem_solve_page(login):
    driver = login
    driver.get(f"{BASE_URL}/problems/{PROBLEM_ID}/solve")
    # Wait for the solve page to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(ProblemSolvePage.CODE_EDITOR)
        )
    except TimeoutException:
        pytest.fail("Problem solve page did not load.")
    return ProblemSolvePage(driver)

# Test Case TC011
def test_submitting_incorrect_code_shows_failed_status(problem_solve_page: ProblemSolvePage):
    """
    TC011: Submitting incorrect code shows failed status
    """
    # Incorrect solution (e.g., always returns 0 instead of expected sum)
    incorrect_code = """
def solve(a, b):
    return 0
"""

    # Write incorrect code
    problem_solve_page.write_code(incorrect_code)

    # Submit the code
    problem_solve_page.submit()

    # Verify "Submission evaluated" message appears
    try:
        message = problem_solve_page.get_message()
        assert "Submission evaluated" in message, f"Unexpected message: {message}"
    except TimeoutException:
        pytest.fail("Submission message did not appear within timeout.")

    # Verify status shows "Failed"
    try:
        status = problem_solve_page.get_status()
        assert status == "Failed", f"Expected status 'Failed', got '{status}'"
    except TimeoutException:
        pytest.fail("Status element did not appear within timeout.")

    # Verify result displays the incorrect output
    try:
        result = problem_solve_page.get_result()
        # The result should contain the incorrect output, e.g., "0" or a mismatch message
        assert result != "Correct", f"Result should not be 'Correct', got '{result}'"
        assert "0" in result or "does not match" in result, f"Result does not indicate incorrect output: {result}"
    except TimeoutException:
        pytest.fail("Result element did not appear within timeout.")