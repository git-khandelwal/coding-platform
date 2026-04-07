import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# ------------------------------
# Page Object Model
# ------------------------------
class HomePage:
    """Page object for the application's home page."""

    URL = "http://localhost:5000/"

    # Locators
    LOGIN_USERNAME = (By.ID, "login-username")
    LOGIN_PASSWORD = (By.ID, "login-password")
    LOGIN_BUTTON = (By.XPATH, "//form[@id='login-form']//button")
    ERROR_MESSAGE = (By.XPATH, "//*[contains(text(),'Invalid username or password')]")

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def open(self):
        """Navigate to the home page."""
        self.driver.get(self.URL)

    def login(self, username: str, password: str):
        """Enter credentials and submit the login form."""
        try:
            self.wait.until(EC.presence_of_element_located(self.LOGIN_USERNAME)).clear()
            self.driver.find_element(*self.LOGIN_USERNAME).send_keys(username)

            self.wait.until(EC.presence_of_element_located(self.LOGIN_PASSWORD)).clear()
            self.driver.find_element(*self.LOGIN_PASSWORD).send_keys(password)

            self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON)).click()
        except TimeoutException as e:
            raise AssertionError(f"Login form elements not found: {e}")

    def get_error_message(self) -> str:
        """Retrieve the error message displayed after a failed login attempt."""
        try:
            element = self.wait.until(
                EC.visibility_of_element_located(self.ERROR_MESSAGE)
            )
            return element.text
        except TimeoutException:
            raise AssertionError("Error message not displayed within timeout.")


# ------------------------------
# Pytest Fixtures
# ------------------------------
@pytest.fixture(scope="function")
def driver():
    """Set up and tear down the Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1280, 800)
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def home_page(driver):
    """Instantiate the HomePage object."""
    return HomePage(driver)


# ------------------------------
# Test Case: TC004
# ------------------------------
def test_login_failure_incorrect_credentials(home_page: HomePage):
    """
    TC004: Login failure with incorrect credentials
    Verify that logging in with wrong credentials shows an error message.
    """
    # Preconditions: A user must be registered. For the purpose of this test,
    # we assume the username "existing_user" exists in the system.
    username = "existing_user"
    wrong_password = "wrong_password"

    # Step 1: Open the home page
    home_page.open()

    # Step 2: Enter an existing username with an incorrect password
    home_page.login(username, wrong_password)

    # Step 3: Click the "Login" button (already done in login method)

    # Expected Result: Error message “Invalid username or password” is displayed.
    error_text = home_page.get_error_message()
    assert error_text == "Invalid username or password", (
        f"Expected error message not found. Got: '{error_text}'"
    )