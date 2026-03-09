import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Page Object for Add Problem Page ---
class AddProblemPage:
    URL = "http://localhost:5000/problems/add"

    # Locators for required fields
    TITLE_INPUT = (By.ID, "title")
    DESCRIPTION_INPUT = (By.ID, "description")
    DIFFICULTY_INPUT = (By.ID, "difficulty")
    INPUT_FORMAT_INPUT = (By.ID, "input_format")
    OUTPUT_FORMAT_INPUT = (By.ID, "output_format")
    SAMPLE_INPUT_INPUT = (By.ID, "sample_input")
    SAMPLE_OUTPUT_INPUT = (By.ID, "sample_output")
    SAMPLE_CODE_INPUT = (By.ID, "sample_code")
    CONSTRAINTS_INPUT = (By.ID, "constraints")

    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(self.URL)

    def wait_for_page(self):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.TITLE_INPUT)
        )

    def is_field_visible(self, locator):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(locator)
            )
            return element.is_displayed()
        except Exception:
            return False

    def all_fields_visible(self):
        return all([
            self.is_field_visible(self.TITLE_INPUT),
            self.is_field_visible(self.DESCRIPTION_INPUT),
            self.is_field_visible(self.DIFFICULTY_INPUT),
            self.is_field_visible(self.INPUT_FORMAT_INPUT),
            self.is_field_visible(self.OUTPUT_FORMAT_INPUT),
            self.is_field_visible(self.SAMPLE_INPUT_INPUT),
            self.is_field_visible(self.SAMPLE_OUTPUT_INPUT),
            self.is_field_visible(self.SAMPLE_CODE_INPUT),
            self.is_field_visible(self.CONSTRAINTS_INPUT),
        ])

# --- Pytest Fixtures ---
@pytest.fixture(scope="function")
def driver():
    # Setup: Start browser
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    # Teardown: Quit browser
    driver.quit()

@pytest.fixture(scope="function")
def authenticated_driver(driver):
    # Setup: Authenticate user before accessing add problem page
    # This assumes a test user exists with username 'testuser' and password 'testpass'
    driver.get("http://localhost:5000/login")
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "login-username"))
    )
    driver.find_element(By.ID, "login-username").send_keys("testuser")
    driver.find_element(By.ID, "login-password").send_keys("testpass")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    # Wait for login to complete (could check for redirect or protected content)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "protected-button"))
    )
    return driver

# --- Test Case TC014 ---
def test_tc014_add_problem_page_field_presence(authenticated_driver):
    """
    TC014: Verify that the add problem page displays all required fields for problem creation.
    """
    page = AddProblemPage(authenticated_driver)
    page.open()
    page.wait_for_page()

    assert page.is_field_visible(page.TITLE_INPUT), "Title field is not visible"
    assert page.is_field_visible(page.DESCRIPTION_INPUT), "Description field is not visible"
    assert page.is_field_visible(page.DIFFICULTY_INPUT), "Difficulty field is not visible"
    assert page.is_field_visible(page.INPUT_FORMAT_INPUT), "Input format field is not visible"
    assert page.is_field_visible(page.OUTPUT_FORMAT_INPUT), "Output format field is not visible"
    assert page.is_field_visible(page.SAMPLE_INPUT_INPUT), "Sample input field is not visible"
    assert page.is_field_visible(page.SAMPLE_OUTPUT_INPUT), "Sample output field is not visible"
    assert page.is_field_visible(page.SAMPLE_CODE_INPUT), "Sample code field is not visible"
    assert page.is_field_visible(page.CONSTRAINTS_INPUT), "Constraints field is not visible"