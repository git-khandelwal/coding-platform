import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Page Objects ---

class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    def login(self, username, password):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-form"))
        )
        self.driver.find_element(By.ID, "login-username").clear()
        self.driver.find_element(By.ID, "login-username").send_keys(username)
        self.driver.find_element(By.ID, "login-password").clear()
        self.driver.find_element(By.ID, "login-password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "#login-form button[type='submit']").click()

class AddProblemPage:
    def __init__(self, driver):
        self.driver = driver

    def is_loaded(self):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )

    def fill_form(self, title, description, difficulty, input_format, output_format, sample_input, sample_output, sample_code, constraints):
        self.driver.find_element(By.NAME, "title").send_keys(title)
        self.driver.find_element(By.NAME, "description").send_keys(description)
        self.driver.find_element(By.NAME, "difficulty").send_keys(difficulty)
        self.driver.find_element(By.NAME, "input_format").send_keys(input_format)
        self.driver.find_element(By.NAME, "output_format").send_keys(output_format)
        self.driver.find_element(By.NAME, "sample_input").send_keys(sample_input)
        self.driver.find_element(By.NAME, "sample_output").send_keys(sample_output)
        self.driver.find_element(By.NAME, "sample_code").send_keys(sample_code)
        self.driver.find_element(By.NAME, "constraints").send_keys(constraints)

    def submit(self):
        self.driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()

class ProblemsListPage:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_list(self):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".problems-list, table, ul"))
        )

    def problem_exists(self, title):
        # Try to find the problem by title in the list
        try:
            elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{title}')]")
            return any(title in el.text for el in elements)
        except Exception:
            return False

# --- Fixtures and Test ---

@pytest.fixture(scope="session")
def selenium_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def create_and_login_user(selenium_driver):
    # Register a new user
    selenium_driver.get("http://localhost:5000/")
    username = f"testuser_tc024_{int(time.time())}"
    password = "TestPassword123!"

    # Register
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_element_located((By.ID, "register-form"))
    )
    selenium_driver.find_element(By.ID, "register-username").clear()
    selenium_driver.find_element(By.ID, "register-username").send_keys(username)
    selenium_driver.find_element(By.ID, "register-password").clear()
    selenium_driver.find_element(By.ID, "register-password").send_keys(password)
    selenium_driver.find_element(By.CSS_SELECTOR, "#register-form button[type='submit']").click()

    # Wait for registration to complete (assume a notification or redirect)
    time.sleep(1)

    # Login
    login_page = LoginPage(selenium_driver)
    login_page.login(username, password)

    # Wait for login to complete (assume a notification or redirect)
    time.sleep(1)

    return username, password

def test_tc024_add_new_problem_authenticated_user(selenium_driver, create_and_login_user):
    # Step 1: User is already logged in via fixture

    # Step 2: Navigate to add problem page
    selenium_driver.get("http://localhost:5000/problems/add")
    add_problem_page = AddProblemPage(selenium_driver)
    assert add_problem_page.is_loaded(), "Add Problem form did not load"

    # Step 3: Fill out problem form
    test_title = f"Test Problem TC024 {int(time.time())}"
    add_problem_page.fill_form(
        title=test_title,
        description="This is a test problem for TC024.",
        difficulty="Easy",
        input_format="Input: integer n",
        output_format="Output: integer n+1",
        sample_input="1",
        sample_output="2",
        sample_code="print(int(input())+1)",
        constraints="1 <= n <= 100"
    )

    # Step 4: Submit form
    add_problem_page.submit()

    # Wait for redirect or confirmation (assume redirect to problems list)
    WebDriverWait(selenium_driver, 10).until(
        EC.url_contains("/problems")
    )

    # Step 5: Verify problem appears in list
    problems_list_page = ProblemsListPage(selenium_driver)
    problems_list_page.wait_for_list()
    assert problems_list_page.problem_exists(test_title), f"Problem '{test_title}' not found in list after creation"