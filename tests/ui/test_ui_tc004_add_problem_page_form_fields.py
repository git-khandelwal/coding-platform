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
        self.login_form = (By.ID, "login-form")
        self.submit_button = (By.CSS_SELECTOR, "#login-form button[type='submit']")

    def login(self, username, password):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.username_input)
        ).send_keys(username)
        self.driver.find_element(*self.password_input).send_keys(password)
        self.driver.find_element(*self.submit_button).click()
        # Wait for login to complete (e.g., presence of addProblemLink)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "addProblemLink"))
        )

class ProblemsPage:
    def __init__(self, driver):
        self.driver = driver
        self.add_problem_link = (By.ID, "addProblemLink")

    def go_to_add_problem(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.add_problem_link)
        ).click()
        # Wait for navigation to add problem page
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "problemForm"))
        )

class AddProblemPage:
    def __init__(self, driver):
        self.driver = driver
        self.form = (By.ID, "problemForm")
        self.title = (By.ID, "title")
        self.description = (By.ID, "description")
        self.difficulty = (By.ID, "difficulty")
        self.input_format = (By.ID, "input_format")
        self.output_format = (By.ID, "output_format")
        self.sample_input = (By.ID, "sample_input")
        self.sample_output = (By.ID, "sample_output")
        self.sample_code = (By.ID, "sample_code")
        self.constraints = (By.ID, "constraints")

    def required_fields(self):
        # Returns a dict of field id to required attribute bool
        fields = [
            self.title,
            self.description,
            self.difficulty,
            self.input_format,
            self.output_format,
            self.sample_input,
            self.sample_output,
            self.constraints,
        ]
        result = {}
        for locator in fields:
            el = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(locator)
            )
            result[locator[1]] = el.get_attribute("required") is not None
        # sample_code is optional
        code_el = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(self.sample_code)
        )
        result[self.sample_code[1]] = code_el.get_attribute("required") is not None
        return result

    def all_fields_present(self):
        locators = [
            self.title,
            self.description,
            self.difficulty,
            self.input_format,
            self.output_format,
            self.sample_input,
            self.sample_output,
            self.sample_code,
            self.constraints,
        ]
        for locator in locators:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(locator)
            )

# --- Fixtures ---

@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1280,1024")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)
    yield driver
    driver.quit()

@pytest.fixture
def login(driver):
    driver.get("http://localhost:5000/")
    login_page = LoginPage(driver)
    login_page.login("test", "1234")
    return ProblemsPage(driver)

@pytest.fixture
def add_problem_page(driver, login):
    problems_page = login
    problems_page.go_to_add_problem()
    return AddProblemPage(driver)

# --- Test Case TC004 ---

def test_add_problem_form_fields_present_and_required(add_problem_page):
    # Check all fields are present
    add_problem_page.all_fields_present()
    required = add_problem_page.required_fields()
    # Required fields
    assert required["title"], "Title field should be required"
    assert required["description"], "Description field should be required"
    assert required["difficulty"], "Difficulty field should be required"
    assert required["input_format"], "Input format field should be required"
    assert required["output_format"], "Output format field should be required"
    assert required["sample_input"], "Sample input field should be required"
    assert required["sample_output"], "Sample output field should be required"
    assert required["constraints"], "Constraints field should be required"
    # Optional field
    assert not required["sample_code"], "Sample code field should NOT be required"