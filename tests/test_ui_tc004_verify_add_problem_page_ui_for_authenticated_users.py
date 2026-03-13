import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Page Objects ---

class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    def open(self, base_url):
        self.driver.get(f"{base_url}/")
    
    def login(self, username, password):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login-form"))
        )
        self.driver.find_element(By.ID, "login-username").send_keys(username)
        self.driver.find_element(By.ID, "login-password").send_keys(password)
        self.driver.find_element(By.ID, "login-form").submit()

class ProblemsPage:
    def __init__(self, driver):
        self.driver = driver

    def open(self, base_url):
        self.driver.get(f"{base_url}/problems")
    
    def click_add_problem(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "addProblemLink"))
        )
        self.driver.find_element(By.ID, "addProblemLink").click()

class AddProblemPage:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_load(self):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "problemForm"))
        )

    def is_field_visible(self, field_id):
        try:
            elem = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, field_id))
            )
            return elem.is_displayed()
        except Exception:
            return False

# --- Fixtures ---

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def base_url():
    # Adjust as needed for your environment
    return "http://localhost:5000"

@pytest.fixture(scope="function")
def authenticated_user(driver, base_url):
    login_page = LoginPage(driver)
    login_page.open(base_url)
    # Use a valid test user; ensure this user exists in your test DB
    login_page.login("testuser", "testpassword")
    # Wait for login to complete (e.g., presence of protected content)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "protected-content"))
    )
    return driver

# --- Test Case TC004 ---

def test_tc004_add_problem_page_ui_authenticated(authenticated_user, base_url):
    driver = authenticated_user
    problems_page = ProblemsPage(driver)
    add_problem_page = AddProblemPage(driver)

    # Step 2: Navigate to add problem page
    problems_page.open(base_url)
    problems_page.click_add_problem()

    # Step 3: Observe input fields
    add_problem_page.wait_for_load()

    required_fields = [
        "title",
        "description",
        "difficulty",
        "input_format",
        "output_format",
        "sample_input",
        "sample_output",
        "sample_code",
        "constraints"
    ]

    for field_id in required_fields:
        assert add_problem_page.is_field_visible(field_id), f"Field '{field_id}' not visible on Add Problem page"