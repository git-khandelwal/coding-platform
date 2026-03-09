import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Page Objects ---

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.username_input = (By.ID, "login-username")
        self.password_input = (By.ID, "login-password")
        self.login_button = (By.XPATH, "//form[@id='login-form']//button[@type='submit']")

    def load(self, base_url):
        self.driver.get(base_url)

    def login(self, username, password):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.username_input)
        ).send_keys(username)
        self.driver.find_element(*self.password_input).send_keys(password)
        self.driver.find_element(*self.login_button).click()

class ProblemManagementPage:
    def __init__(self, driver):
        self.driver = driver
        self.problem_rows = (By.CSS_SELECTOR, ".problem-row")
        self.edit_buttons = (By.CSS_SELECTOR, ".problem-row .edit-problem-btn")
        self.delete_buttons = (By.CSS_SELECTOR, ".problem-row .delete-problem-btn")

    def load(self, base_url):
        self.driver.get(f"{base_url}/problems/manage")

    def wait_for_problems(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.problem_rows)
        )

    def get_edit_buttons(self):
        return self.driver.find_elements(*self.edit_buttons)

    def get_delete_buttons(self):
        return self.driver.find_elements(*self.delete_buttons)

# --- Fixtures ---

@pytest.fixture(scope="session")
def base_url():
    # Change this to the actual running app URL if needed
    return "http://localhost:5000"

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1280, 1024)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def authenticated_user(driver, base_url):
    # Credentials for an existing test user with problem management access
    username = "testadmin"
    password = "testpassword"
    login_page = LoginPage(driver)
    login_page.load(base_url)
    login_page.login(username, password)
    # Wait for login to complete (could be a redirect or a UI change)
    WebDriverWait(driver, 10).until(
        lambda d: d.current_url != f"{base_url}/"
    )
    return driver

# --- Test Case TC016 ---

def test_edit_delete_buttons_visible_for_authenticated_user_TC016(authenticated_user, base_url):
    """
    TC016: Verify that edit and delete options are available for authenticated users on problem management pages.
    Steps:
    1. Log in as an authenticated user.
    2. Navigate to a problem management page.
    3. Observe the available actions.
    Expected:
    1. Edit and delete buttons are visible for each problem.
    """
    driver = authenticated_user
    problem_management_page = ProblemManagementPage(driver)
    # Try both likely URLs for management page
    management_urls = [f"{base_url}/problems/manage", f"{base_url}/problems"]
    found = False
    for url in management_urls:
        driver.get(url)
        try:
            problem_management_page.wait_for_problems()
            found = True
            break
        except Exception:
            continue
    assert found, "Problem management page did not load or no problems present."

    # Check that for each problem row, edit and delete buttons are present
    problem_rows = driver.find_elements(*problem_management_page.problem_rows)
    assert problem_rows, "No problems found on the management page."

    edit_buttons = problem_management_page.get_edit_buttons()
    delete_buttons = problem_management_page.get_delete_buttons()

    assert len(edit_buttons) == len(problem_rows), (
        f"Expected {len(problem_rows)} edit buttons, found {len(edit_buttons)}"
    )
    assert len(delete_buttons) == len(problem_rows), (
        f"Expected {len(problem_rows)} delete buttons, found {len(delete_buttons)}"
    )

    # Additionally, check that each button is visible
    for btn in edit_buttons + delete_buttons:
        assert btn.is_displayed(), "Edit/Delete button is not visible for a problem."