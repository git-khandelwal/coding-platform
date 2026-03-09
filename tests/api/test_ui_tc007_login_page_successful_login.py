import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from playwright.sync_api import sync_playwright

LOGIN_URL = "http://localhost:5000/"  # Adjust if login page is at a different path
VALID_USERNAME = "testuser_tc007"
VALID_PASSWORD = "testpass_tc007"

# --- Selenium Page Object ---
class LoginPageSelenium:
    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(LOGIN_URL)

    def enter_username(self, username):
        username_input = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login-username"))
        )
        username_input.clear()
        username_input.send_keys(username)

    def enter_password(self, password):
        password_input = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login-password"))
        )
        password_input.clear()
        password_input.send_keys(password)

    def submit(self):
        login_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//form[@id='login-form']//button[@type='submit']"))
        )
        login_button.click()

    def wait_for_login_success(self):
        # Wait for either a redirect or a success indicator/message
        try:
            WebDriverWait(self.driver, 10).until(
                EC.url_changes(LOGIN_URL)
            )
            return True
        except:
            # Check for success message in page
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'success')]"))
                )
                return True
            except:
                return False

# --- Playwright Page Object ---
class LoginPagePlaywright:
    def __init__(self, page):
        self.page = page

    def open(self):
        self.page.goto(LOGIN_URL)

    def enter_username(self, username):
        self.page.wait_for_selector("#login-username")
        self.page.fill("#login-username", username)

    def enter_password(self, password):
        self.page.wait_for_selector("#login-password")
        self.page.fill("#login-password", password)

    def submit(self):
        self.page.click("form#login-form button[type='submit']")

    def wait_for_login_success(self):
        try:
            self.page.wait_for_url(lambda url: url != LOGIN_URL, timeout=10000)
            return True
        except:
            try:
                self.page.wait_for_selector("text=success", timeout=5000)
                return True
            except:
                return False

# --- Helper: Register user if not exists ---
def ensure_user_registered(username, password):
    import requests
    resp = requests.post(
        f"{LOGIN_URL.rstrip('/')}/register",
        json={"username": username, "password": password}
    )
    # 201 = success, 400 = already exists
    if resp.status_code not in (201, 400):
        raise Exception(f"User registration failed: {resp.text}")

# --- Selenium Fixtures ---
@pytest.fixture(scope="module")
def selenium_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

# --- Playwright Fixtures ---
@pytest.fixture(scope="module")
def playwright_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture(scope="module")
def playwright_page(playwright_browser):
    page = playwright_browser.new_page()
    yield page
    page.close()

# --- Test Case: TC007 Selenium ---
def test_tc007_login_success_selenium(selenium_driver):
    ensure_user_registered(VALID_USERNAME, VALID_PASSWORD)
    login_page = LoginPageSelenium(selenium_driver)
    login_page.open()
    login_page.enter_username(VALID_USERNAME)
    login_page.enter_password(VALID_PASSWORD)
    login_page.submit()
    assert login_page.wait_for_login_success(), "Login was not successful (Selenium)"

# --- Test Case: TC007 Playwright ---
def test_tc007_login_success_playwright(playwright_page):
    ensure_user_registered(VALID_USERNAME, VALID_PASSWORD)
    login_page = LoginPagePlaywright(playwright_page)
    login_page.open()
    login_page.enter_username(VALID_USERNAME)
    login_page.enter_password(VALID_PASSWORD)
    login_page.submit()
    assert login_page.wait_for_login_success(), "Login was not successful (Playwright)"