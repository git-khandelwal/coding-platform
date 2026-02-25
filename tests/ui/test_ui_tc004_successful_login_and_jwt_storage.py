import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

# Page Object Model for the Home Page
class HomePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open(self):
        self.driver.get(BASE_URL)

    def _login_form(self):
        return self.wait.until(EC.presence_of_element_located((By.ID, "login-form")))

    def _register_form(self):
        return self.wait.until(EC.presence_of_element_located((By.ID, "register-form")))

    def _protected_button(self):
        return self.wait.until(EC.element_to_be_clickable((By.ID, "protected-button")))

    def login(self, username, password):
        try:
            form = self._login_form()
            username_input = form.find_element(By.ID, "login-username")
            password_input = form.find_element(By.ID, "login-password")
            submit_button = form.find_element(By.XPATH, ".//button[@type='submit']")

            username_input.clear()
            username_input.send_keys(username)
            password_input.clear()
            password_input.send_keys(password)
            submit_button.click()
        except (TimeoutException, NoSuchElementException) as e:
            pytest.fail(f"Login form interaction failed: {e}")

    def get_local_storage_item(self, key):
        try:
            # Execute JavaScript to retrieve localStorage item
            script = f"return window.localStorage.getItem('{key}');"
            return self.driver.execute_script(script)
        except Exception as e:
            pytest.fail(f"Failed to read localStorage: {e}")

    def click_protected_button(self):
        try:
            button = self._protected_button()
            button.click()
        except (TimeoutException, NoSuchElementException) as e:
            pytest.fail(f"Protected button interaction failed: {e}")

    def get_protected_content_text(self):
        try:
            # After clicking the protected button, the response is displayed in #protected-content
            content = self.wait.until(EC.presence_of_element_located((By.ID, "protected-content")))
            return content.text
        except (TimeoutException, NoSuchElementException) as e:
            pytest.fail(f"Protected content not found: {e}")

# Pytest fixture for Selenium WebDriver
@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)
    yield driver
    driver.quit()

# Test case TC004: Successful login and JWT storage
def test_tc004_successful_login_and_jwt_storage(driver):
    page = HomePage(driver)

    # Step 1: Open the root URL
    page.open()

    # Step 2: Enter username and password
    page.login("fortnite", "fortnite")

    # Step 3: Verify that the login succeeded by checking for the presence of the protected button
    try:
        page._protected_button()
    except TimeoutException:
        pytest.fail("Login failed: Protected button not visible after login")

    # Step 4: Check localStorage for access_token
    token = page.get_local_storage_item("access_token")
    assert token is not None and token != "", "access_token not found in localStorage after login"

    # Step 5: Click the "Protected content test" button
    page.click_protected_button()

    # Verify that the protected content displays "logged_in_as: fortnite"
    content_text = page.get_protected_content_text()
    assert "logged_in_as: fortnite" in content_text, f"Unexpected protected content: {content_text}"