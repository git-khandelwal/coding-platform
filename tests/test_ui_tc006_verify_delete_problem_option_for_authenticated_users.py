import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from playwright.sync_api import sync_playwright

# --- Selenium Page Objects ---

class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    def login(self, username, password):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login-form"))
        )
        self.driver.find_element(By.ID, "login-username").clear()
        self.driver.find_element(By.ID, "login-username").send_keys(username)
        self.driver.find_element(By.ID, "login-password").clear()
        self.driver.find_element(By.ID, "login-password").send_keys(password)
        self.driver.find_element(By.ID, "login-form").submit()

class ProblemDetailsPage:
    def __init__(self, driver):
        self.driver = driver

    def is_delete_button_visible(self):
        try:
            delete_btn = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "deleteProblemButton"))
            )
            return delete_btn.is_displayed()
        except Exception:
            return False

# --- Selenium Fixtures ---

@pytest.fixture(scope="function")
def selenium_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

# --- Selenium Test ---

def test_tc006_delete_option_visible_selenium(selenium_driver):
    selenium_driver.get("http://localhost:5000/")
    login_page = LoginPage(selenium_driver)
    login_page.login("testuser", "testpass")  # Replace with valid credentials

    # Navigate to a specific problem details page (example problem id: 1)
    selenium_driver.get("http://localhost:5000/problems/1")
    problem_page = ProblemDetailsPage(selenium_driver)
    assert problem_page.is_delete_button_visible(), "Delete button should be visible for authenticated user with permission"

# --- Playwright Fixtures ---

@pytest.fixture(scope="function")
def playwright_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        yield context
        context.close()
        browser.close()

# --- Playwright Page Objects ---

class PlaywrightLoginPage:
    def __init__(self, page):
        self.page = page

    def login(self, username, password):
        self.page.wait_for_selector("#login-form", timeout=10000)
        self.page.fill("#login-username", username)
        self.page.fill("#login-password", password)
        self.page.click("#login-form button[type='submit']")

class PlaywrightProblemDetailsPage:
    def __init__(self, page):
        self.page = page

    def is_delete_button_visible(self):
        try:
            self.page.wait_for_selector("#deleteProblemButton", timeout=10000)
            return self.page.is_visible("#deleteProblemButton")
        except Exception:
            return False

# --- Playwright Test ---

def test_tc006_delete_option_visible_playwright(playwright_context):
    page = playwright_context.new_page()
    page.goto("http://localhost:5000/")
    login_page = PlaywrightLoginPage(page)
    login_page.login("testuser", "testpass")  # Replace with valid credentials

    page.goto("http://localhost:5000/problems/1")
    problem_page = PlaywrightProblemDetailsPage(page)
    assert problem_page.is_delete_button_visible(), "Delete button should be visible for authenticated user with permission"
    page.close()