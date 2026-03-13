import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LOGIN_URL = "http://localhost:5000/"  # Adjust if your login page is at a different URL

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    @property
    def username_field(self):
        return self.wait.until(
            EC.presence_of_element_located((By.ID, "login-username"))
        )

    @property
    def password_field(self):
        return self.wait.until(
            EC.presence_of_element_located((By.ID, "login-password"))
        )

    @property
    def login_button(self):
        # Look for a button inside the login form
        form = self.wait.until(
            EC.presence_of_element_located((By.ID, "login-form"))
        )
        return form.find_element(By.TAG_NAME, "button")

@pytest.fixture(scope="function")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

def test_TC006_login_form_fields_present(driver):
    driver.get(LOGIN_URL)
    login_page = LoginPage(driver)

    # Assert username field is present
    try:
        username_input = login_page.username_field
        assert username_input.is_displayed(), "Username input field is not displayed"
    except Exception as e:
        pytest.fail(f"Username input field not found or not visible: {e}")

    # Assert password field is present
    try:
        password_input = login_page.password_field
        assert password_input.is_displayed(), "Password input field is not displayed"
    except Exception as e:
        pytest.fail(f"Password input field not found or not visible: {e}")

    # Assert login button is present
    try:
        login_btn = login_page.login_button
        assert login_btn.is_displayed(), "Login button is not displayed"
    except Exception as e:
        pytest.fail(f"Login button not found or not visible: {e}")