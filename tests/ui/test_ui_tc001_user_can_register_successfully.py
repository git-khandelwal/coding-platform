import uuid
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


# Page Object for the Home Page
class HomePage:
    URL = "http://localhost:5000/"  # Adjust if the app runs on a different host/port

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def load(self):
        self.driver.get(self.URL)

    def register(self, username, password):
        # Wait for the register form to be present
        self.wait.until(EC.presence_of_element_located((By.ID, "register-form")))
        # Fill in username
        username_input = self.driver.find_element(By.ID, "register-username")
        username_input.clear()
        username_input.send_keys(username)
        # Fill in password
        password_input = self.driver.find_element(By.ID, "register-password")
        password_input.clear()
        password_input.send_keys(password)
        # Submit the form
        register_button = self.driver.find_element(By.XPATH, "//form[@id='register-form']//button[@type='submit']")
        register_button.click()

    def get_success_message(self):
        # Wait for the success message to appear in the response
        # Assuming the server returns JSON and the page displays it in an alert or a div
        # Since the template doesn't show a success element, we will poll the network response via JS
        # For simplicity, we will check for an element that appears after successful registration
        # We'll use a custom div with id 'success-message' that the backend might render
        try:
            element = self.wait.until(
                EC.visibility_of_element_located((By.ID, "success-message"))
            )
            return element.text
        except:
            return None

    def is_form_cleared(self):
        username_value = self.driver.find_element(By.ID, "register-username").get_attribute("value")
        password_value = self.driver.find_element(By.ID, "register-password").get_attribute("value")
        return username_value == "" and password_value == ""


@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


def test_user_can_register_successfully(driver):
    """
    Test Case ID: TC001
    Summary: User can register successfully
    """
    home_page = HomePage(driver)
    home_page.load()

    # Generate a unique username
    unique_username = f"user_{uuid.uuid4().hex[:8]}"
    password = "TestPass123!"

    # Perform registration
    home_page.register(unique_username, password)

    # Verify success message
    success_text = home_page.get_success_message()
    assert success_text == "User registered successfully", f"Expected success message not found. Got: {success_text}"

    # Verify form fields are cleared
    assert home_page.is_form_cleared(), "Form fields were not cleared after registration"

    # Optional: Verify that the user is now present in the database via API call
    # This part is omitted as it requires backend access, but could be added if needed.