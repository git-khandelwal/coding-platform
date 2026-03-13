import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LOGIN_URL = "http://localhost:5000/"  # Adjust if app runs on a different port

INVALID_USERNAME = "invalid_user"
INVALID_PASSWORD = "wrong_password"

ERROR_MESSAGE_TEXTS = [
    "Invalid username or password",
    "invalid username or password",
    "Invalid credentials",
    "invalid credentials"
]

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def load(self):
        self.driver.get(LOGIN_URL)
        self.wait.until(EC.visibility_of_element_located((By.ID, "login-form")))

    def set_username(self, username):
        username_input = self.wait.until(EC.visibility_of_element_located((By.ID, "login-username")))
        username_input.clear()
        username_input.send_keys(username)

    def set_password(self, password):
        password_input = self.wait.until(EC.visibility_of_element_located((By.ID, "login-password")))
        password_input.clear()
        password_input.send_keys(password)

    def submit(self):
        form = self.driver.find_element(By.ID, "login-form")
        # Try to find a submit button within the form, fallback to pressing Enter
        try:
            submit_btn = form.find_element(By.XPATH, ".//button[@type='submit' or contains(text(),'Login') or contains(text(),'Sign in')]")
            submit_btn.click()
        except Exception:
            # Fallback: submit by pressing Enter in password field
            password_input = form.find_element(By.ID, "login-password")
            password_input.send_keys(Keys.ENTER)

    def get_error_message(self):
        # Try to find a visible error message after failed login
        # Common patterns: <div class="error">, <span class="error">, or alert
        possible_selectors = [
            (By.XPATH, "//*[contains(@class, 'error') and string-length(normalize-space(text())) > 0]"),
            (By.XPATH, "//*[contains(@class, 'alert') and string-length(normalize-space(text())) > 0]"),
            (By.XPATH, "//*[contains(text(), 'Invalid')]"),
            (By.XPATH, "//*[contains(text(), 'invalid')]"),
            (By.XPATH, "//form[@id='login-form']//div[string-length(normalize-space(text())) > 0]"),
        ]
        for by, selector in possible_selectors:
            try:
                elem = self.wait.until(EC.visibility_of_element_located((by, selector)))
                text = elem.text.strip()
                if text:
                    return text
            except Exception:
                continue
        # If not found, return empty string
        return ""

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1200,800")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

def test_TC008_login_error_message_on_failed_login(driver):
    """
    TC008: Authentication - Error Message on Failed Login
    Steps:
      1. Navigate to the login page.
      2. Enter invalid username/password.
      3. Submit the form.
    Expected:
      1. An error message is shown indicating invalid credentials.
      2. User is not logged in.
    """
    login_page = LoginPage(driver)
    login_page.load()
    login_page.set_username(INVALID_USERNAME)
    login_page.set_password(INVALID_PASSWORD)
    login_page.submit()

    # Wait for error message or for the form to remain visible
    error_text = login_page.get_error_message()

    # Assert error message is shown and contains expected text
    assert any(msg.lower() in error_text.lower() for msg in ERROR_MESSAGE_TEXTS), \
        f"Expected error message about invalid credentials, got: '{error_text}'"

    # Assert user is not logged in (login form should still be visible)
    assert driver.find_element(By.ID, "login-form").is_displayed(), \
        "Login form should still be visible after failed login."