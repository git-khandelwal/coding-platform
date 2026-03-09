import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

# --- Page Object for Problems List Page ---
class ProblemsListPage:
    URL = "http://localhost:5000/problems"

    def __init__(self, driver):
        self.driver = driver

    def load(self):
        self.driver.get(self.URL)

    def is_loaded(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            return True
        except Exception:
            return False

    def problems_list_is_visible(self):
        try:
            ul = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "problemsList"))
            )
            # Wait for at least one problem in the list (li element)
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#problemsList li"))
            )
            return True
        except Exception:
            return False

    def login_form_present(self):
        # There should be no login form on this page
        try:
            self.driver.find_element(By.ID, "login-form")
            return True
        except Exception:
            return False

# --- Fixtures for Setup and Teardown ---
@pytest.fixture(scope="function")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = ChromeService()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1280, 1024)
    yield driver
    driver.quit()

# --- Test Case TC008 ---
def test_problems_list_page_accessible_and_displays_problems(driver):
    """
    TC008: Problems List Page - Accessibility
    1. Navigate to the problems list page.
    2. Observe the content.
    Expected:
    - List of coding problems is visible.
    - Page loads without requiring login.
    """
    problems_page = ProblemsListPage(driver)
    problems_page.load()

    assert problems_page.is_loaded(), "Problems list page did not load properly (missing <h1>)."

    assert problems_page.problems_list_is_visible(), "Problems list is not visible or contains no problems."

    assert not problems_page.login_form_present(), "Login form should not be present on the problems list page (should not require authentication)."