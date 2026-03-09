import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

REGISTER_URL = "http://localhost:5000/"  # Adjust if your app runs elsewhere
EXISTING_USERNAME = "already_registered_user"
VALID_PASSWORD = "ValidPass123!"

class RegistrationPage:
    def __init__(self, driver):
        self.driver = driver
        self.username_input = (By.ID, "register-username")
        self.password_input = (By.ID, "register-password")
        self.submit_button = (By.XPATH, "//form[@id='register-form']//button[@type='submit']")
        self.form = (By.ID, "register-form")

    def open(self):
        self.driver.get(REGISTER_URL)

    def set_username(self, username):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.username_input)
        ).clear()
        self.driver.find_element(*self.username_input).send_keys(username)

    def set_password(self, password):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.password_input)
        ).clear()
        self.driver.find_element(*self.password_input).send_keys(password)

    def submit(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.submit_button)
        ).click()

    def get_error_message(self):
        # Error message is likely rendered after form submit, but no specific selector is given.
        # Try to find a visible element containing the error message.
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Username already exists')]"))
            ).text
        except Exception:
            return None

@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1200, 900)
    yield driver
    driver.quit()

@pytest.fixture(scope="session", autouse=True)
def ensure_existing_user():
    """
    Ensure the EXISTING_USERNAME is registered before the test.
    """
    import requests
    url = REGISTER_URL.rstrip("/") + "/register"
    # Try to register the user via API
    try:
        requests.post(
            url,
            json={"username": EXISTING_USERNAME, "password": VALID_PASSWORD},
            timeout=5
        )
    except Exception:
        pass  # If server is unreachable, the test will fail later

def test_registration_existing_username_shows_error(driver, ensure_existing_user):
    """
    TC003: Verify that attempting to register with an existing username displays an error message.
    """
    page = RegistrationPage(driver)
    page.open()
    page.set_username(EXISTING_USERNAME)
    page.set_password(VALID_PASSWORD)
    page.submit()
    error_text = page.get_error_message()
    assert error_text is not None, "Expected error message not displayed"
    assert "Username already exists" in error_text