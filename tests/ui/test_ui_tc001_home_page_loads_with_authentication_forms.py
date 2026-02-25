import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import os

# Page Object Model for the Home Page
class HomePage:
    URL = os.getenv("BASE_URL", "http://localhost:5000/")  # Adjust as needed

    # Locators
    REGISTER_FORM = (By.ID, "register-form")
    LOGIN_FORM = (By.ID, "login-form")
    PROBLEMS_LINK = (By.XPATH, "//a[contains(@href, '/problems')]")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def load(self):
        self.driver.get(self.URL)

    def is_register_form_visible(self):
        try:
            self.wait.until(EC.visibility_of_element_located(self.REGISTER_FORM))
            return True
        except TimeoutException:
            return False

    def is_login_form_visible(self):
        try:
            self.wait.until(EC.visibility_of_element_located(self.LOGIN_FORM))
            return True
        except TimeoutException:
            return False

    def is_problems_link_visible_and_clickable(self):
        try:
            link = self.wait.until(EC.element_to_be_clickable(self.PROBLEMS_LINK))
            return link.is_displayed()
        except TimeoutException:
            return False

# Pytest fixture for Selenium WebDriver
@pytest.fixture(scope="module")
def driver():
    # Set up Chrome WebDriver (ensure chromedriver is in PATH)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run headless for CI
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = ChromeService()
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)
    yield driver
    driver.quit()

# Test case TC001
def test_home_page_loads_with_auth_forms(driver):
    """
    TC001: Home page loads with authentication forms
    """
    home = HomePage(driver)
    home.load()

    # Verify registration form is visible
    assert home.is_register_form_visible(), "Registration form should be visible on the home page."

    # Verify login form is visible
    assert home.is_login_form_visible(), "Login form should be visible on the home page."

    # Verify Problems link is present and clickable
    assert home.is_problems_link_visible_and_clickable(), "Problems link should be present and clickable."

    # Optional: click the Problems link to ensure navigation works
    try:
        problems_link = driver.find_element(*HomePage.PROBLEMS_LINK)
        problems_link.click()
        # Wait for the new page to load by checking the URL contains '/problems'
        WebDriverWait(driver, 10).until(EC.url_contains("/problems"))
    except (NoSuchElementException, TimeoutException) as e:
        pytest.fail(f"Failed to navigate to Problems page: {e}")