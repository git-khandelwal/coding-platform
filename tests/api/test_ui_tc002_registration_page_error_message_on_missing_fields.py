import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Page Object for Registration Page ---

class RegistrationPage:
    URL = "http://localhost:5000/"  # Adjust as needed

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

    def submit_registration(self, username=None, password=None):
        if username is not None:
            self.username_input.clear()
            self.username_input.send_keys(username)
        else:
            self.username_input.clear()
        if password is not None:
            self.password_input.clear()
            self.password_input.send_keys(password)
        else:
            self.password_input.clear()
        self.register_button.click()

    def get_error_message(self):
        # The error message is not rendered in the DOM, but returned as a JSON response.
        # So, we need to intercept the network response or check for a visible error.
        # However, in the default template, there is no error display.
        # For the sake of this test, let's assume the app shows an alert with the error.
        try:
            WebDriverWait(self.driver, 2).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            text = alert.text
            alert.accept()
            return text
        except Exception:
            # If no alert, check for error message in the page (if implemented)
            try:
                error_elem = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Username and password are required')]")
                return error_elem.text
            except Exception:
                return None

# --- Fixtures ---

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def registration_page(driver):
    page = RegistrationPage(driver)
    page.open()
    return page

# --- Test Case TC002 ---

def test_registration_missing_fields_shows_error_message_tc002(registration_page):
    # Step 1: Navigate to the registration page (done in fixture)
    # Step 2: Leave both fields empty and submit
    registration_page.submit_registration(username=None, password=None)

    # Step 3: Wait for error message
    error_text = None
    try:
        error_text = WebDriverWait(registration_page.driver, 3).until(
            lambda d: registration_page.get_error_message()
        )
    except Exception:
        error_text = registration_page.get_error_message()

    assert error_text is not None, "Expected error message was not displayed"
    assert "Username and password are required" in error_text