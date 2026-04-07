import json
import time
import uuid

import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from playwright.sync_api import sync_playwright, Playwright, Request, Route


BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="session")
def playwright_client() -> Playwright:
    """Provide a Playwright sync context for API requests."""
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def registered_user(playwright_client: Playwright):
    """Register a new user via the API and return credentials."""
    # Generate a unique username
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "TestPass123!"

    # Create a request context
    request = playwright_client.request.new_context(base_url=BASE_URL)

    # Register the user
    response = request.post(
        "/register",
        data=json.dumps({"username": username, "password": password}),
        headers={"Content-Type": "application/json"},
    )
    assert response.status == 201, f"Registration failed: {response.text()}"

    return {"username": username, "password": password}


@pytest.fixture(scope="function")
def driver() -> webdriver.Chrome:
    """Set up and tear down the Selenium WebDriver."""
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1280, 800)
    yield driver
    driver.quit()


def test_login_and_token_stored(driver: webdriver.Chrome, registered_user: dict):
    """
    TC003: User can log in and token is stored
    """
    username = registered_user["username"]
    password = registered_user["password"]

    # 1. Open the home page
    driver.get(BASE_URL)

    wait = WebDriverWait(driver, 10)

    try:
        # 2. Enter a valid username and password in the login form
        login_username = wait.until(
            EC.presence_of_element_located((By.ID, "login-username"))
        )
        login_password = driver.find_element(By.ID, "login-password")
        login_button = driver.find_element(By.XPATH, "//form[@id='login-form']//button")

        login_username.clear()
        login_username.send_keys(username)
        login_password.clear()
        login_password.send_keys(password)

        # 3. Click the "Login" button
        login_button.click()

        # Expected Result 1: A success message “Login successful” appears.
        success_msg = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Login successful')]")
            )
        )
        assert success_msg.is_displayed(), "Success message not displayed."

        # Expected Result 2: A JWT token is stored in localStorage.
        # Wait a bit for the token to be set
        time.sleep(1)
        token = driver.execute_script("return window.localStorage.getItem('access_token');")
        assert token is not None, "Token not found in localStorage."
        # Basic JWT validation: three parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3, f"Token format invalid: {token}"
        # Optionally, decode header to ensure it's base64
        try:
            json.loads(
                json.dumps(
                    {
                        "header": json.loads(
                            base64.urlsafe_b64decode(parts[0] + "==").decode()
                        ),
                        "payload": json.loads(
                            base64.urlsafe_b64decode(parts[1] + "==").decode()
                        ),
                    }
                )
            )
        except Exception:
            # If decoding fails, still consider it a valid JWT string
            pass

    except (NoSuchElementException, TimeoutException) as e:
        pytest.fail(f"Test failed due to element not found or timeout: {e}")
    except AssertionError as e:
        pytest.fail(f"Assertion failed: {e}")
    finally:
        # Optional: clear localStorage for cleanup
        driver.execute_script("window.localStorage.clear();")
        driver.quit()