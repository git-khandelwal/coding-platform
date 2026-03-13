import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

BASE_URL = "http://localhost:5000"

USERNAME = "test"
PASSWORD = "1234"

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

class ProblemsListPage:
    def __init__(self, driver):
        self.driver = driver

    def select_first_problem(self):
        # Wait for the problems list to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "View"))
        )
        # Click the first "View" link (assuming each problem has a View link)
        self.driver.find_elements(By.LINK_TEXT, "View")[0].click()

class ProblemDetailsPage:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_page(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "description"))
        )

    def get_problem_fields(self):
        fields = {}
        fields['title'] = self.driver.find_element(By.ID, "title").text if self._element_exists(By.ID, "title") else None
        fields['description'] = self.driver.find_element(By.ID, "description").text if self._element_exists(By.ID, "description") else None
        fields['input_format'] = self.driver.find_element(By.ID, "input_format").text if self._element_exists(By.ID, "input_format") else None
        fields['output_format'] = self.driver.find_element(By.ID, "output_format").text if self._element_exists(By.ID, "output_format") else None
        fields['sample_input'] = self.driver.find_element(By.ID, "sample_input").text if self._element_exists(By.ID, "sample_input") else None
        fields['sample_output'] = self.driver.find_element(By.ID, "sample_output").text if self._element_exists(By.ID, "sample_output") else None
        fields['constraints'] = self.driver.find_element(By.ID, "constraints").text if self._element_exists(By.ID, "constraints") else None
        # sample_code is optional
        fields['sample_code'] = self.driver.find_element(By.ID, "sample_code").text if self._element_exists(By.ID, "sample_code") else None
        return fields

    def _element_exists(self, by, value):
        try:
            self.driver.find_element(by, value)
            return True
        except:
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
def login(driver):
    driver.get(f"{BASE_URL}/")
    login_page = LoginPage(driver)
    login_page.login(USERNAME, PASSWORD)
    # Wait for redirect to problems page or protected content
    try:
        WebDriverWait(driver, 10).until(
            EC.url_contains("/problems")
        )
    except:
        # If not redirected, maybe a protected button/content is shown
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "protected-content"))
        )

# --- Test Case Implementation ---

def test_problem_details_page_content_TC002(driver, login):
    # Go to the problems list page
    driver.get(f"{BASE_URL}/problems")
    problems_list_page = ProblemsListPage(driver)
    problems_list_page.select_first_problem()

    problem_details_page = ProblemDetailsPage(driver)
    problem_details_page.wait_for_page()

    fields = problem_details_page.get_problem_fields()

    # Assert all required fields are present and not empty
    assert fields['title'] is not None and fields['title'].strip() != ""
    assert fields['description'] is not None and fields['description'].strip() != ""
    assert fields['input_format'] is not None and fields['input_format'].strip() != ""
    assert fields['output_format'] is not None and fields['output_format'].strip() != ""
    assert fields['sample_input'] is not None and fields['sample_input'].strip() != ""
    assert fields['sample_output'] is not None and fields['sample_output'].strip() != ""
    assert fields['constraints'] is not None and fields['constraints'].strip() != ""
    # sample_code is optional, but if present, it should not be empty
    if fields['sample_code'] is not None:
        assert fields['sample_code'].strip() != ""