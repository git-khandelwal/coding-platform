import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from playwright.sync_api import sync_playwright

LOGIN_URL = "http://localhost:5000/"  # Adjust if login page is at a different route
INVALID_USERNAME = "invalid_user"
INVALID_PASSWORD = "invalid_pass"

# --- Selenium Page Object ---

class LoginPageSelenium:
    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(LOGIN_URL)

    def enter_username(self, username):
        username_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login-username"))
        )
        username_field.clear()
        username_field.send_keys(username)

    def enter_password(self, password):
        password_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login-password"))
        )
        password_field.clear()
        password_field.send_keys(password)

    def submit(self):
        form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-form"))
        )
        form.submit()

    def get_error_message(self):
        # Wait for error message to appear after failed login
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_any_elements_located((By.XPATH, "//*[contains(text(), 'Invalid username or password')]"))
        )

# --- Selenium Test ---

@pytest.fixture(scope="function")
def selenium_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

def test_tc011_selenium_verify_error_message_on_login_fail(selenium_driver):
    login_page = LoginPageSelenium(selenium_driver)
    login_page.open()
    login_page.enter_username(INVALID_USERNAME)
    login_page.enter_password(INVALID_PASSWORD)
    login_page.submit()
    error_elements = login_page.get_error_message()
    assert any("Invalid username or password" in elem.text for elem in error_elements), "Error message not displayed for invalid credentials"

# --- Playwright Page Object ---

class LoginPagePlaywright:
    def __init__(self, page):
        self.page = page

    def open(self):
        self.page.goto(LOGIN_URL)

    def enter_username(self, username):
        self.page.fill("#login-username", username)

    def enter_password(self, password):
        self.page.fill("#login-password", password)

    def submit(self):
        self.page.locator("#login-form").evaluate("form => form.submit()")

    def get_error_message(self):
        # Wait for error message to appear after failed login
        self.page.wait_for_selector("text=Invalid username or password", timeout=5000)
        return self.page.locator("text=Invalid username or password").inner_text()

# --- Playwright Test ---

@pytest.fixture(scope="function")
def playwright_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        yield page
        context.close()
        browser.close()

def test_tc011_playwright_verify_error_message_on_login_fail(playwright_page):
    login_page = LoginPagePlaywright(playwright_page)
    login_page.open()
    login_page.enter_username(INVALID_USERNAME)
    login_page.enter_password(INVALID_PASSWORD)
    login_page.submit()
    error_message = login_page.get_error_message()
    assert "Invalid username or password" in error_message, "Error message not displayed for invalid credentials"