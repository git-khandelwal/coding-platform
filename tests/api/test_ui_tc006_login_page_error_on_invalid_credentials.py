import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LOGIN_URL = "http://localhost:5000/"  # Adjust if login page is at a different URL

INVALID_USERNAME = "invaliduser"
INVALID_PASSWORD = "invalidpass"

ERROR_MESSAGE_TEXT = "Invalid username or password"

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.username_input = (By.ID, "login-username")
        self.password_input = (By.ID, "login-password")
        self.login_button = (By.XPATH, "//form[@id='login-form']//button[@type='submit']")
        self.form = (By.ID, "login-form")

    def load(self):
        self.driver.get(LOGIN_URL)

    def enter_username(self, username):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.username_input)
        ).clear()
        self.driver.find_element(*self.username_input).send_keys(username)

    def enter_password(self, password):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.password_input)
        ).clear()
        self.driver.find_element(*self.password_input).send_keys(password)

    def submit(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.login_button)
        ).click()

    def wait_for_error_message(self):
        # Since the UI code context does not show an error message element,
        # we must assume the error is shown as an alert or as a new element injected into the DOM.
        # We'll check for a visible element containing the error text.
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(
                    (By.XPATH, f"//*[contains(text(), '{ERROR_MESSAGE_TEXT}')]")
                )
            )
        except Exception:
            # Check if an alert is present
            try:
                alert = WebDriverWait(self.driver, 2).until(EC.alert_is_present())
                return alert
            except Exception:
                return None

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

def test_login_invalid_credentials_shows_error_message(driver):
    login_page = LoginPage(driver)
    login_page.load()
    login_page.enter_username(INVALID_USERNAME)
    login_page.enter_password(INVALID_PASSWORD)
    login_page.submit()

    error_element = login_page.wait_for_error_message()
    assert error_element is not None, "Error message not displayed for invalid credentials"

    # If error is in alert, check alert text
    if hasattr(error_element, "text"):
        error_text = error_element.text
    else:
        # If it's an alert, get alert text
        try:
            error_text = driver.switch_to.alert.text
        except Exception:
            error_text = ""

    assert ERROR_MESSAGE_TEXT in error_text, f"Expected error message '{ERROR_MESSAGE_TEXT}' not found. Actual: '{error_text}'"