import pytest
import time
import string
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Page Objects ---

class HomePage:
    def __init__(self, driver):
        self.driver = driver
        self.register_form = (By.ID, "register-form")
        self.register_username = (By.ID, "register-username")
        self.register_password = (By.ID, "register-password")
        self.register_button = (By.CSS_SELECTOR, "#register-form button[type='submit']")
        self.login_form = (By.ID, "login-form")
        self.login_username = (By.ID, "login-username")
        self.login_password = (By.ID, "login-password")
        self.login_button = (By.CSS_SELECTOR, "#login-form button[type='submit']")
        self.protected_button = (By.ID, "protected-button")
        self.protected_content = (By.ID, "protected-content")
        self.alerts = (By.CSS_SELECTOR, ".alert, .error, .success")

    def register(self, username, password):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.register_form)
        )
        self.driver.find_element(*self.register_username).clear()
        self.driver.find_element(*self.register_username).send_keys(username)
        self.driver.find_element(*self.register_password).clear()
        self.driver.find_element(*self.register_password).send_keys(password)
        self.driver.find_element(*self.register_button).click()

    def login(self, username, password):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.login_form)
        )
        self.driver.find_element(*self.login_username).clear()
        self.driver.find_element(*self.login_username).send_keys(username)
        self.driver.find_element(*self.login_password).clear()
        self.driver.find_element(*self.login_password).send_keys(password)
        self.driver.find_element(*self.login_button).click()

    def click_protected(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.protected_button)
        )
        self.driver.find_element(*self.protected_button).click()

    def get_protected_content(self):
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self.protected_content)
            ).text
        except Exception:
            return ""

    def get_alert_text(self):
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self.alerts)
            ).text
        except Exception:
            return ""

# --- Fixtures ---

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1280,1024")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(2)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def home_page(driver):
    base_url = "http://localhost:5000/"
    driver.get(base_url)
    return HomePage(driver)

# --- Test Case TC022 ---

def random_username():
    return "testuser_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def random_password():
    return "Testpass1!" + ''.join(random.choices(string.ascii_letters + string.digits, k=5))

def test_tc022_user_registration_login_and_token_usage(driver, home_page):
    username = random_username()
    password = random_password()

    # Step 1: Navigate to home page (done by fixture)

    # Step 2: Register a new user
    home_page.register(username, password)
    # Wait for registration to complete; check for success message or alert
    time.sleep(0.5)
    # Registration may show a message, or just allow login. Try to login regardless.

    # Step 3: Log in with the new user
    home_page.login(username, password)
    # Wait for login to complete; check for JWT token in localStorage/sessionStorage or success message
    # The UI may not display the token, so we check for login success by attempting to access protected content

    # Step 4: Store JWT token (if exposed in JS)
    # Try to extract JWT token from localStorage/sessionStorage if available
    jwt_token = None
    try:
        jwt_token = driver.execute_script("return window.localStorage.getItem('access_token') || window.sessionStorage.getItem('access_token');")
    except Exception:
        pass

    # Step 5: Access protected content
    home_page.click_protected()
    # Wait for protected content to appear
    protected_text = ""
    for _ in range(10):
        protected_text = home_page.get_protected_content()
        if protected_text:
            break
        time.sleep(0.5)

    # --- Assertions ---

    # 1. Registration is successful: user can log in and access protected content
    assert protected_text, "Protected content should be visible after login."

    # 2. Login returns JWT token: if token is exposed in storage, check it's a JWT
    if jwt_token:
        assert jwt_token.count('.') == 2, "JWT token should be present in storage after login."

    # 3. Protected content is accessible with token: check content includes username
    assert username in protected_text, f"Protected content should include username '{username}', got: {protected_text}"