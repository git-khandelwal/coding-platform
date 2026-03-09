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

    def open(self, base_url):
        self.driver.get(base_url)

    def wait_for_registration_fields(self, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        username = wait.until(EC.visibility_of_element_located((By.ID, "register-username")))
        password = wait.until(EC.visibility_of_element_located((By.ID, "register-password")))
        return username, password

# --- Playwright Page Object ---

class RegistrationPagePlaywright:
    def __init__(self, page):
        self.page = page

    def open(self, base_url):
        self.page.goto(base_url)

    def wait_for_registration_fields(self, timeout=10000):
        username = self.page.wait_for_selector("#register-username", state="visible", timeout=timeout)
        password = self.page.wait_for_selector("#register-password", state="visible", timeout=timeout)
        return username, password

# --- Selenium Fixtures and Test ---

@pytest.fixture(scope="function")
def selenium_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(2)
    yield driver
    driver.quit()

def test_TC001_registration_field_presence_selenium(selenium_driver):
    base_url = "http://localhost:5000/"
    reg_page = RegistrationPageSelenium(selenium_driver)
    reg_page.open(base_url)
    username, password = reg_page.wait_for_registration_fields()
    assert username.is_displayed(), "Username input field is not visible"
    assert password.is_displayed(), "Password input field is not visible"

# --- Playwright Fixtures and Test ---

@pytest.fixture(scope="function")
def playwright_page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        yield page
        browser.close()

def test_TC001_registration_field_presence_playwright(playwright_page):
    base_url = "http://localhost:5000/"
    reg_page = RegistrationPagePlaywright(playwright_page)
    reg_page.open(base_url)
    username, password = reg_page.wait_for_registration_fields()
    assert username.is_visible(), "Username input field is not visible"
    assert password.is_visible(), "Password input field is not visible"