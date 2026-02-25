import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://localhost:5000"  # Adjust if your app runs elsewhere


@pytest.fixture(scope="session")
def driver():
    """Initialize and teardown the Selenium WebDriver."""
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


class HomePage:
    """Page Object for the home page containing registration and login forms."""

    REGISTER_FORM = (By.ID, "register-form")
    USERNAME_INPUT = (By.ID, "register-username")
    PASSWORD_INPUT = (By.ID, "register-password")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "#register-form button[type='submit']")
    ERROR_MESSAGE = (By.XPATH, "//*[contains(text(), 'Username and password are required')]")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open(self, url=BASE_URL):
        self.driver.get(url)

    def submit_registration_form(self, username: str = None, password: str = None):
        """Fill in the registration form and submit."""
        if username is not None:
            self.wait.until(EC.element_to_be_clickable(self.USERNAME_INPUT)).clear()
            self.driver.find_element(*self.USERNAME_INPUT).send_keys(username)
        if password is not None:
            self.wait.until(EC.element_to_be_clickable(self.PASSWORD_INPUT)).clear()
            self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
        self.wait.until(EC.element_to_be_clickable(self.SUBMIT_BUTTON)).click()

    def get_error_message(self) -> str:
        """Return the error message text if present."""
        try:
            element = self.wait.until(EC.visibility_of_element_located(self.ERROR_MESSAGE))
            return element.text
        except TimeoutException:
            return ""


def test_registration_form_validation(driver):
    """TC003: Ensure that submitting the registration form with missing fields displays an error."""
    page = HomePage(driver)
    page.open()

    # Leave both fields blank and submit
    page.submit_registration_form()

    # Verify that the page did not navigate away
    assert driver.current_url == f"{BASE_URL}/", "Form submission should not navigate away."

    # Verify that the expected error message is displayed
    error_text = page.get_error_message()
    assert error_text == "Username and password are required", (
        f"Expected error message not found. Got: '{error_text}'"
    )
    # Additional check: form should still be present
    try:
        page.wait.until(EC.presence_of_element_located(HomePage.REGISTER_FORM))
    except TimeoutException:
        pytest.fail("Registration form disappeared after submission.")