import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from playwright.sync_api import sync_playwright

# --- Selenium Page Object ---

class RegistrationPageSelenium:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_page(self):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "register-form"))
        )

    def username_input(self):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "register-username"))
        )

    def password_input(self):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "register-password"))
        )

    def register_button(self):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//form[@id='register-form']//button[@type='submit']"))
        )

# --- Playwright Page Object ---

class RegistrationPagePlaywright:
    def __init__(self, page):
        self.page = page

    def wait_for_page(self):
        self.page.wait_for_selector("#register-form", state="visible", timeout=10000)

    def username_input(self):
        return self.page.locator("#register-username")

    def password_input(self):
        return self.page.locator("#register-password")

    def register_button(self):
        return self.page.locator("#register-form button[type='submit']")

# --- Selenium Fixtures ---

@pytest.fixture(scope="function")
def selenium_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

# --- Playwright Fixtures ---

@pytest.fixture(scope="function")
def playwright_page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        yield page
        browser.close()

# --- Selenium Test ---

def test_TC008_registration_page_ui_selenium(selenium_driver):
    selenium_driver.get("http://localhost:5000/")  # Adjust if app runs elsewhere
    reg_page = RegistrationPageSelenium(selenium_driver)
    reg_page.wait_for_page()

    assert reg_page.username_input().is_displayed(), "Username input not visible"
    assert reg_page.password_input().is_displayed(), "Password input not visible"
    assert reg_page.register_button().is_displayed(), "Register button not visible"

# --- Playwright Test ---

def test_TC008_registration_page_ui_playwright(playwright_page):
    playwright_page.goto("http://localhost:5000/")  # Adjust if app runs elsewhere
    reg_page = RegistrationPagePlaywright(playwright_page)
    reg_page.wait_for_page()

    assert reg_page.username_input().is_visible(), "Username input not visible"
    assert reg_page.password_input().is_visible(), "Password input not visible"
    assert reg_page.register_button().is_visible(), "Register button not visible"