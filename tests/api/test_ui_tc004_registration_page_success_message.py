import pytest
import string
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Page Object Model for Registration Page ---

class RegistrationPage:
    URL = "http://localhost:5000/"  # Adjust if running on a different port

    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(self.URL)

    @property
    def username_input(self):
        return self.driver.find_element(By.ID, "register-username")

    @property
    def password_input(self):
        return self.driver.find_element(By.ID, "register-password")

    @property
    def register_button(self):
        return self.driver.find_element(By.CSS_SELECTOR, "#register-form button[type='submit']")

    @property
    def register_form(self):
        return self.driver.find_element(By.ID, "register-form")

    def fill_registration_form(self, username, password):
        self.username_input.clear()
        self.username_input.send_keys(username)
        self.password_input.clear()
        self.password_input.send_keys(password)

    def submit_registration(self):
        self.register_button.click()

    def wait_for_success_message(self, timeout=10):
        # Success message is likely displayed as an alert or in-page message after registration
        # Since the code context does not show where/how the message is rendered,
        # we'll check for a browser alert first, then for a visible message in the DOM.
        try:
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            text = alert.text
            alert.accept()
            return text
        except:
            # Try to find in-page message (assume it's rendered somewhere after the form)
            try:
                # Look for a generic message element
                msg = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'User registered successfully')]"))
                )
                return msg.text
            except Exception as e:
                raise AssertionError("Success message not found after registration.") from e

# --- Fixtures for Setup and Teardown ---

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

@pytest.fixture
def registration_page(driver):
    return RegistrationPage(driver)

# --- Utility Function to Generate Unique Username ---

def generate_unique_username():
    return "testuser_" + ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# --- Test Case Implementation ---

def test_TC004_registration_success_message(registration_page):
    """
    TC004: Registration Page - Success Message
    Verify that a successful registration displays a confirmation message.
    """
    # Step 1: Navigate to the registration page
    registration_page.open()

    # Step 2: Enter a unique username and valid password
    username = generate_unique_username()
    password = "ValidPass123!"

    registration_page.fill_registration_form(username, password)

    # Step 3: Submit the form
    registration_page.submit_registration()

    # Expected Result: Message "User registered successfully" is displayed
    success_message = registration_page.wait_for_success_message(timeout=10)
    assert "User registered successfully" in success_message