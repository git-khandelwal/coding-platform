import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Page Object for Login Page
class LoginPage:
    LOGIN_FORM_ID = "login-form"
    USERNAME_INPUT_ID = "login-username"
    PASSWORD_INPUT_ID = "login-password"

    def __init__(self, driver):
        self.driver = driver

    def wait_for_login_form(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.ID, self.LOGIN_FORM_ID))
        )

    def is_username_field_visible(self, timeout=10):
        try:
            username_input = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.ID, self.USERNAME_INPUT_ID))
            )
            return username_input.is_displayed()
        except Exception:
            return False

    def is_password_field_visible(self, timeout=10):
        try:
            password_input = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.ID, self.PASSWORD_INPUT_ID))
            )
            return password_input.is_displayed()
        except Exception:
            return False

# Fixture for Selenium WebDriver setup and teardown
@pytest.fixture(scope="function")
def driver():
    # You may need to adjust the executable_path for your environment
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

# Test Case TC005: Login Page - Field Presence
def test_tc005_login_page_field_presence(driver):
    # Adjust URL if needed
    LOGIN_PAGE_URL = "http://localhost:5000/"
    driver.get(LOGIN_PAGE_URL)

    login_page = LoginPage(driver)
    login_page.wait_for_login_form()

    assert login_page.is_username_field_visible(), "Username input field is not visible on the login page."
    assert login_page.is_password_field_visible(), "Password input field is not visible on the login page."