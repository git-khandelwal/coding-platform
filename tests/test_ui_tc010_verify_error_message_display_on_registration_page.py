import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from playwright.sync_api import sync_playwright

# ----------- SELENIUM PAGE OBJECTS -----------

class RegistrationPageSelenium:
    def __init__(self, driver):
        self.driver = driver
        self.url = "http://localhost:5000/"
        self.register_form_id = "register-form"
        self.username_id = "register-username"
        self.password_id = "register-password"
        self.submit_button_selector = "#register-form button[type='submit']"

    def load(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, self.register_form_id))
        )

    def submit_registration(self, username="", password=""):
        username_input = self.driver.find_element(By.ID, self.username_id)
        password_input = self.driver.find_element(By.ID, self.password_id)
        username_input.clear()
        password_input.clear()
        if username:
            username_input.send_keys(username)
        if password:
            password_input.send_keys(password)
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, self.submit_button_selector)
        submit_btn.click()

    def get_error_message(self):
        try:
            error_elem = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'error') or contains(text(), 'error')]"))
            )
            return error_elem.text
        except Exception:
            # Try to find error message in alert or other common places
            try:
                alert_elem = self.driver.find_element(By.XPATH, "//div[contains(text(), 'required') or contains(text(), 'exists')]")
                return alert_elem.text
            except Exception:
                return ""

# ----------- PLAYWRIGHT PAGE OBJECTS -----------

class RegistrationPagePlaywright:
    def __init__(self, page):
        self.page = page
        self.url = "http://localhost:5000/"
        self.register_form_id = "#register-form"
        self.username_id = "#register-username"
        self.password_id = "#register-password"
        self.submit_button_selector = "#register-form button[type='submit']"

    def load(self):
        self.page.goto(self.url)
        self.page.wait_for_selector(self.register_form_id)

    def submit_registration(self, username="", password=""):
        self.page.fill(self.username_id, username)
        self.page.fill(self.password_id, password)
        self.page.click(self.submit_button_selector)

    def get_error_message(self):
        try:
            # Try to find error message in a div with error class or containing error text
            error_elem = self.page.wait_for_selector("div.error, div:has-text('error'), div:has-text('required'), div:has-text('exists')", timeout=3000)
            return error_elem.text_content()
        except Exception:
            return ""

# ----------- SELENIUM TEST FIXTURES -----------

@pytest.fixture(scope="function")
def selenium_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

# ----------- PLAYWRIGHT TEST FIXTURES -----------

@pytest.fixture(scope="function")
def playwright_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()

# ----------- SELENIUM TEST CASE -----------

def test_TC010_registration_error_messages_selenium(selenium_driver):
    page = RegistrationPageSelenium(selenium_driver)
    page.load()

    # Step 2: Attempt to register with missing fields
    page.submit_registration(username="", password="")
    error_msg_missing = page.get_error_message()
    assert "required" in error_msg_missing.lower() or "username and password" in error_msg_missing.lower(), \
        f"Expected error for missing fields, got: {error_msg_missing}"

    # Step 3: Attempt to register with an existing username
    # First, register a user (if not already exists)
    unique_username = "testuser_tc010"
    page.submit_registration(username=unique_username, password="password123")
    # Wait for possible success or error
    # Try again with same username
    page.load()
    page.submit_registration(username=unique_username, password="password123")
    error_msg_duplicate = page.get_error_message()
    assert "exists" in error_msg_duplicate.lower() or "already" in error_msg_duplicate.lower(), \
        f"Expected error for duplicate username, got: {error_msg_duplicate}"

# ----------- PLAYWRIGHT TEST CASE -----------

def test_TC010_registration_error_messages_playwright(playwright_page):
    page = RegistrationPagePlaywright(playwright_page)
    page.load()

    # Step 2: Attempt to register with missing fields
    page.submit_registration(username="", password="")
    error_msg_missing = page.get_error_message()
    assert error_msg_missing is not None
    assert "required" in error_msg_missing.lower() or "username and password" in error_msg_missing.lower(), \
        f"Expected error for missing fields, got: {error_msg_missing}"

    # Step 3: Attempt to register with an existing username
    unique_username = "testuser_tc010_pw"
    page.submit_registration(username=unique_username, password="password123")
    # Wait for possible success or error
    page.load()
    page.submit_registration(username=unique_username, password="password123")
    error_msg_duplicate = page.get_error_message()
    assert error_msg_duplicate is not None
    assert "exists" in error_msg_duplicate.lower() or "already" in error_msg_duplicate.lower(), \
        f"Expected error for duplicate username, got: {error_msg_duplicate}"