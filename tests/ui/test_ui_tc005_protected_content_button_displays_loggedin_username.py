import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from playwright.sync_api import sync_playwright

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------
@pytest.fixture(scope="session")
def base_url():
    """Base URL of the application under test."""
    return "http://localhost:5000"

@pytest.fixture(scope="function")
def driver():
    """Selenium WebDriver fixture with headless Chrome."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

# ----------------------------------------------------------------------
# Page Objects
# ----------------------------------------------------------------------
class HomePage:
    """Page Object for the Home page."""

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 15)

    def open(self):
        """Navigate to the home page."""
        self.driver.get(self.base_url)

    def login(self, username: str, password: str):
        """Log in using the provided credentials."""
        try:
            self.wait.until(EC.visibility_of_element_located((By.ID, "login-username")))
            username_input = self.driver.find_element(By.ID, "login-username")
            password_input = self.driver.find_element(By.ID, "login-password")
            login_button = self.driver.find_element(By.XPATH, "//form[@id='login-form']//button")

            username_input.clear()
            username_input.send_keys(username)
            password_input.clear()
            password_input.send_keys(password)
            login_button.click()

            # Wait until the protected button becomes clickable, indicating login success
            self.wait.until(EC.element_to_be_clickable((By.ID, "protected-button")))
        except (TimeoutException, NoSuchElementException) as e:
            raise AssertionError(f"Login failed or elements not found: {e}")

    def click_protected_button(self):
        """Click the 'Test JWT' (protected content) button."""
        try:
            protected_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "protected-button")))
            protected_btn.click()
        except (TimeoutException, NoSuchElementException) as e:
            raise AssertionError(f"Protected button not clickable: {e}")

    def get_protected_content_message(self) -> str:
        """Retrieve the message displayed after clicking the protected button."""
        try:
            content_el = self.wait.until(EC.visibility_of_element_located((By.ID, "protected-content")))
            return content_el.text.strip()
        except (TimeoutException, NoSuchElementException) as e:
            raise AssertionError(f"Protected content message not found: {e}")

    def get_token_from_localstorage(self) -> str:
        """Retrieve the JWT token stored in localStorage."""
        token = self.driver.execute_script("return localStorage.getItem('access_token');")
        if not token:
            raise AssertionError("JWT token not found in localStorage")
        return token

# ----------------------------------------------------------------------
# Test Case: TC005
# ----------------------------------------------------------------------
def test_tc005_protected_content_displays_username(driver, base_url):
    """
    TC005: Verify that clicking the protected content button after login shows the logged‑in username.
    """
    username = "testuser"
    password = "testpass"

    page = HomePage(driver, base_url)
    page.open()
    page.login(username, password)
    page.click_protected_button()

    # Verify UI message
    ui_message = page.get_protected_content_message()
    expected_ui = f"Logged in as {username}"
    assert expected_ui in ui_message, f"UI message '{ui_message}' does not contain expected '{expected_ui}'"

    # Verify backend response using Playwright
    token = page.get_token_from_localstorage()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        try:
            response = context.request.get(
                f"{base_url}/protected",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.ok, f"API request failed with status {response.status}"
            json_body = response.json()
            api_username = json_body.get("logged_in_as")
            assert api_username == username, (
                f"API returned username '{api_username}', expected '{username}'"
            )
        finally:
            browser.close()