import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:5000"  # Adjust to your test server URL


class HomePage:
    """Page Object for the application's home page."""

    # Locators
    REGISTER_FORM = (By.ID, "register-form")
    USERNAME_INPUT = (By.ID, "register-username")
    PASSWORD_INPUT = (By.ID, "register-password")
    REGISTER_BUTTON = (By.CSS_SELECTOR, "#register-form button[type='submit']")
    SUCCESS_MESSAGE = (By.XPATH, "//*[contains(text(),'User registered successfully')]")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def load(self):
        self.driver.get(BASE_URL)

    def register(self, username: str, password: str):
        """Fill the registration form and submit."""
        self.wait.until(EC.visibility_of_element_located(self.REGISTER_FORM))
        self.driver.find_element(*self.USERNAME_INPUT).clear()
        self.driver.find_element(*self.USERNAME_INPUT).send_keys(username)
        self.driver.find_element(*self.PASSWORD_INPUT).clear()
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
        self.driver.find_element(*self.REGISTER_BUTTON).click()

    def wait_for_success(self):
        """Wait until the success message is visible."""
        return self.wait.until(EC.visibility_of_element_located(self.SUCCESS_MESSAGE))

    def is_on_home_page(self):
        """Verify that the current URL is the home page."""
        return self.driver.current_url.rstrip("/") == BASE_URL.rstrip("/")


@pytest.fixture(scope="session")
def driver():
    """Set up the Selenium WebDriver."""
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)
    yield driver
    driver.quit()


@pytest.fixture
def home_page(driver):
    """Instantiate the HomePage object."""
    return HomePage(driver)


def test_successful_user_registration(home_page):
    """
    TC002: Successful user registration
    Verify that a new user can register via the registration form and receives a success message.
    """
    # Arrange
    unique_username = f"testuser_{int(time.time() * 1000)}"
    password = "TestPass123!"

    # Act
    home_page.load()
    home_page.register(unique_username, password)

    # Assert
    try:
        success_element = home_page.wait_for_success()
        assert success_element is not None, "Success message not found."
        assert "User registered successfully" in success_element.text
        assert home_page.is_on_home_page(), "User did not remain on the home page after registration."
    except Exception as e:
        pytest.fail(f"Test failed due to exception: {e}")