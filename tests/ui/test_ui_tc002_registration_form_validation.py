import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Page Object Model for the Home Page
class HomePage:
    URL = "http://localhost:5000/"  # Adjust if the app runs on a different host/port

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def open(self):
        self.driver.get(self.URL)

    def click_register(self):
        try:
            register_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#register-form button[type='submit']"))
            )
            register_button.click()
        except TimeoutException:
            raise AssertionError("Register button not clickable within timeout")

    def get_error_message(self):
        try:
            error_element = self.wait.until(
                EC.visibility_of_element_located((By.ID, "register-error"))
            )
            return error_element.text.strip()
        except TimeoutException:
            # If the error element never appears, return None
            return None

# Pytest fixture for Selenium WebDriver setup and teardown
@pytest.fixture(scope="function")
def driver():
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

# Test case TC002: Registration form validation
def test_registration_form_validation(driver):
    """
    TC002: Verify that the registration form shows an error message
    when both username and password fields are left empty.
    """
    home = HomePage(driver)
    home.open()

    # Ensure the form is present
    try:
        driver.find_element(By.ID, "register-form")
    except NoSuchElementException:
        pytest.fail("Registration form not found on the home page")

    # Leave username and password empty and click Register
    home.click_register()

    # Verify the error message
    error_msg = home.get_error_message()
    assert error_msg is not None, "Error message element did not appear"
    assert error_msg == "Username and password are required", (
        f"Unexpected error message: '{error_msg}'"
    )