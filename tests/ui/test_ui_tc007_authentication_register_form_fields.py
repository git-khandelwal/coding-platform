import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Page Object for Registration Form ---

class RegisterPage:
    def __init__(self, driver):
        self.driver = driver

    @property
    def register_form(self):
        return self.driver.find_element(By.ID, "register-form")

    @property
    def username_field(self):
        return self.driver.find_element(By.ID, "register-username")

    @property
    def password_field(self):
        return self.driver.find_element(By.ID, "register-password")

    @property
    def register_button(self):
        # Assume the register button is the only button inside the register form
        return self.register_form.find_element(By.TAG_NAME, "button")

    def wait_until_loaded(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.ID, "register-form"))
        )
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.ID, "register-username"))
        )
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.ID, "register-password"))
        )
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.TAG_NAME, "button"))
        )

# --- Pytest Fixtures ---

@pytest.fixture(scope="function")
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1200,800")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(2)
    yield driver
    driver.quit()

@pytest.fixture
def register_page(driver):
    # Assuming the registration form is on the home page (index.html)
    driver.get("http://localhost:5000/")
    page = RegisterPage(driver)
    page.wait_until_loaded()
    return page

# --- Test Case Implementation ---

def test_TC007_register_form_fields_present(register_page):
    """
    TC007: Authentication - Register Form Fields
    Verify that the registration page contains input fields for username and password,
    and a register button is available.
    """
    # Check username field
    username = register_page.username_field
    assert username.is_displayed(), "Username field is not displayed"
    assert username.get_attribute("name") == "username", "Username field should have name='username'"

    # Check password field
    password = register_page.password_field
    assert password.is_displayed(), "Password field is not displayed"
    assert password.get_attribute("name") == "password", "Password field should have name='password'"

    # Check register button
    button = register_page.register_button
    assert button.is_displayed(), "Register button is not displayed"
    # Optionally check button text
    assert "register" in button.text.lower(), "Register button text should contain 'register'"