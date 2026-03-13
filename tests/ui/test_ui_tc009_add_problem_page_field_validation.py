import pytest
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

class ProblemsPage:
    def __init__(self, driver):
        self.driver = driver

    def go_to_add_problem(self):
        add_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "addProblemLink"))
        )
        add_link.click()

class AddProblemPage:
    def __init__(self, driver):
        self.driver = driver

    def submit_with_missing_required_fields(self):
        # Leave 'title' and 'description' empty, fill others minimally
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "problemForm"))
        )
        self.driver.find_element(By.ID, "difficulty").send_keys("Easy")
        self.driver.find_element(By.ID, "input_format").send_keys("Input format")
        self.driver.find_element(By.ID, "output_format").send_keys("Output format")
        self.driver.find_element(By.ID, "sample_input").send_keys("1 2")
        self.driver.find_element(By.ID, "sample_output").send_keys("3")
        self.driver.find_element(By.ID, "sample_code").send_keys("print(sum(map(int, input().split())))")
        self.driver.find_element(By.ID, "constraints").send_keys("1 <= a, b <= 1000")
        # Submit the form
        self.driver.find_element(By.CSS_SELECTOR, "#problemForm button[type='submit']").click()

    def get_validation_errors(self):
        # Try to find validation errors for required fields
        errors = []
        # Check for HTML5 validation bubbles or custom error messages
        # Try to check for :invalid fields
        for field_id in ["title", "description"]:
            field = self.driver.find_element(By.ID, field_id)
            if field.get_attribute("required") is not None:
                # Try to submit again and catch validation
                if not field.get_attribute("value"):
                    errors.append(field_id)
        return errors

# --- Fixtures ---

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def login(driver):
    driver.get("http://localhost:5000/")
    login_page = LoginPage(driver)
    login_page.login("test", "1234")
    # Wait for login to complete (look for protected content or addProblemLink)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "addProblemLink"))
    )

# --- Test Case ---

def test_TC009_add_problem_required_field_validation(driver, login):
    problems_page = ProblemsPage(driver)
    problems_page.go_to_add_problem()
    add_problem_page = AddProblemPage(driver)
    add_problem_page.submit_with_missing_required_fields()

    # Wait a moment for validation to trigger
    WebDriverWait(driver, 2).until(
        lambda d: d.find_element(By.ID, "problemForm")
    )

    # HTML5 validation will prevent form submission if required fields are missing
    # So we expect to still be on the same page, and fields 'title' and 'description' are empty
    errors = add_problem_page.get_validation_errors()
    assert "title" in errors, "Title field should be required and empty"
    assert "description" in errors, "Description field should be required and empty"
    # Optionally, check that URL has not changed (still on add problem)
    assert "/problems/add" in driver.current_url, "Should not navigate away if required fields are missing"