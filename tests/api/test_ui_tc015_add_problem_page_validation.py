import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Page Object for Add Problem Page ---

class AddProblemPage:
    URL = "http://localhost:5000/problems/add"

    # Locators (update as per actual HTML IDs/names/classes)
    TITLE_INPUT = (By.ID, "title")
    DESCRIPTION_INPUT = (By.ID, "description")
    DIFFICULTY_INPUT = (By.ID, "difficulty")
    INPUT_FORMAT_INPUT = (By.ID, "input_format")
    OUTPUT_FORMAT_INPUT = (By.ID, "output_format")
    SAMPLE_INPUT_INPUT = (By.ID, "sample_input")
    SAMPLE_OUTPUT_INPUT = (By.ID, "sample_output")
    SAMPLE_CODE_INPUT = (By.ID, "sample_code")
    CONSTRAINTS_INPUT = (By.ID, "constraints")
    SUBMIT_BUTTON = (By.XPATH, "//button[@type='submit']")
    ERROR_MESSAGE = (By.CLASS_NAME, "error-message")  # Update as per actual error message class

    def __init__(self, driver):
        self.driver = driver

    def load(self):
        self.driver.get(self.URL)

    def clear_required_fields(self):
        # Leave title and description empty (assuming these are required)
        # Fill other fields with dummy data if needed
        # If the form requires all fields, leave only title empty
        pass  # Intentionally leave required fields empty

    def submit_form(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.SUBMIT_BUTTON)
        ).click()

    def get_error_message(self):
        try:
            return WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.ERROR_MESSAGE)
            ).text
        except Exception:
            return None

# --- Pytest Fixtures ---

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def authenticated_session(driver):
    # This fixture assumes that authentication is required to access /problems/add
    # Replace with actual login steps as per your application
    driver.get("http://localhost:5000/login")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "login-username"))
    )
    driver.find_element(By.ID, "login-username").send_keys("admin")
    driver.find_element(By.ID, "login-password").send_keys("adminpassword")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    # Wait for login to complete, e.g., by checking for a known element
    WebDriverWait(driver, 10).until(
        EC.url_changes("http://localhost:5000/login")
    )
    return driver

# --- Test Case TC015 ---

def test_add_problem_required_field_validation(authenticated_session):
    driver = authenticated_session
    add_problem_page = AddProblemPage(driver)
    add_problem_page.load()

    # Wait for the form to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//form"))
    )

    # Leave required fields empty and submit
    add_problem_page.clear_required_fields()
    add_problem_page.submit_form()

    # Assert error message is displayed for missing required fields
    error_message = add_problem_page.get_error_message()
    assert error_message is not None and error_message.strip() != "", \
        "Expected error message for missing required fields, but none was displayed."