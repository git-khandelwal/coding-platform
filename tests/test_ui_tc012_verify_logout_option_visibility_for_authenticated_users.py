import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Page Object for Index (Login/Register/Home)
class IndexPage:
    def __init__(self, driver):
        self.driver = driver

    def open(self, base_url):
        self.driver.get(base_url)

    def login(self, username, password):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login-form"))
        )
        self.driver.find_element(By.ID, "login-username").clear()
        self.driver.find_element(By.ID, "login-username").send_keys(username)
        self.driver.find_element(By.ID, "login-password").clear()
        self.driver.find_element(By.ID, "login-password").send_keys(password)
        self.driver.find_element(By.ID, "login-form").submit()

    def logout_option_visible(self):
        # Try to find logout option by link text or button text
        try:
            logout_link = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//a[contains(translate(text(),'LOGOUT','logout'),'logout')] | //button[contains(translate(text(),'LOGOUT','logout'),'logout')]"
                    )
                )
            )
            return logout_link.is_displayed()
        except Exception:
            return False

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def test_user():
    # This fixture assumes a user with these credentials exists.
    # If not, registration can be automated here.
    return {
        "username": "testuser_tc012",
        "password": "TestPass123!"
    }

@pytest.fixture(scope="function")
def ensure_user_exists(driver, test_user):
    page = IndexPage(driver)
    page.open("http://localhost:5000/")
    try:
        # Try to register user, ignore if already exists
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "register-form"))
        )
        driver.find_element(By.ID, "register-username").clear()
        driver.find_element(By.ID, "register-username").send_keys(test_user["username"])
        driver.find_element(By.ID, "register-password").clear()
        driver.find_element(By.ID, "register-password").send_keys(test_user["password"])
        driver.find_element(By.ID, "register-form").submit()
        # Wait for registration result (ignore errors)
        WebDriverWait(driver, 3).until(
            EC.any_of(
                EC.visibility_of_element_located((By.ID, "login-form")),
                EC.visibility_of_element_located((By.ID, "register-form"))
            )
        )
    except Exception:
        pass

@pytest.mark.tc012
def test_logout_option_visible_for_authenticated_user(driver, test_user, ensure_user_exists):
    page = IndexPage(driver)
    page.open("http://localhost:5000/")
    page.login(test_user["username"], test_user["password"])
    # Wait for login to complete (look for protected content or change in UI)
    try:
        WebDriverWait(driver, 10).until(
            EC.any_of(
                EC.visibility_of_element_located((By.ID, "protected-content")),
                EC.visibility_of_element_located((By.ID, "protected-button"))
            )
        )
    except Exception:
        pass
    # Assert logout option is visible
    assert page.logout_option_visible(), "Logout option should be visible for authenticated users"