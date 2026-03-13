import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from playwright.sync_api import sync_playwright

LOGIN_PAGE_URL = "http://localhost:5000/"  # Adjust if needed

# --- Selenium Page Object ---
class LoginPageSelenium:
    def __init__(self, driver):
        self.driver = driver

    def load(self):
        self.driver.get(LOGIN_PAGE_URL)

    def wait_for_login_form(self):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login-form"))
        )

    def username_input(self):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login-username"))
        )

    def password_input(self):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login-password"))
        )

    def login_button(self):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#login-form button[type='submit']"))
        )

# --- Playwright Page Object ---
class LoginPagePlaywright:
    def __init__(self, page):
        self.page = page

    def load(self):
        self.page.goto(LOGIN_PAGE_URL)

    def wait_for_login_form(self):
        self.page.wait_for_selector("#login-form", state="visible", timeout=10000)

    def username_input(self):
        return self.page.locator("#login-username")

    def password_input(self):
        return self.page.locator("#login-password")

    def login_button(self):
        return self.page.locator("#login-form button[type='submit']")

# --- Selenium Fixtures ---
@pytest.fixture(scope="function")
def selenium_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(3)
    yield driver
    driver.quit()

# --- Playwright Fixtures ---
@pytest.fixture(scope="function")
def playwright_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()

# --- Selenium Test ---
def test_TC009_login_page_ui_selenium(selenium_driver):
    login_page = LoginPageSelenium(selenium_driver)
    login_page.load()
    login_page.wait_for_login_form()

    assert login_page.username_input().is_displayed(), "Username input not visible"
    assert login_page.password_input().is_displayed(), "Password input not visible"
    assert login_page.login_button().is_displayed(), "Login button not visible"

# --- Playwright Test ---
def test_TC009_login_page_ui_playwright(playwright_page):
    login_page = LoginPagePlaywright(playwright_page)
    login_page.load()
    login_page.wait_for_login_form()

    assert login_page.username_input().is_visible(), "Username input not visible"
    assert login_page.password_input().is_visible(), "Password input not visible"
    assert login_page.login_button().is_visible(), "Login button not visible"