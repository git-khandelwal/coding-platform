import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

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
        add_problem_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "addProblemLink"))
        )
        add_problem_link.click()


class AddProblemPage:
    def __init__(self, driver):
        self.driver = driver

    def fill_required_fields_and_submit(self, title, description, difficulty, input_format, output_format, sample_input, sample_output, constraints):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "problemForm"))
        )
        self.driver.find_element(By.ID, "title").send_keys(title)
        self.driver.find_element(By.ID, "description").send_keys(description)
        self.driver.find_element(By.ID, "difficulty").send_keys(difficulty)
        self.driver.find_element(By.ID, "input_format").send_keys(input_format)
        self.driver.find_element(By.ID, "output_format").send_keys(output_format)
        self.driver.find_element(By.ID, "sample_input").send_keys(sample_input)
        self.driver.find_element(By.ID, "sample_output").send_keys(sample_output)
        self.driver.find_element(By.ID, "constraints").send_keys(constraints)
        # Do NOT fill sample_code (leave it empty)
        self.driver.find_element(By.CSS_SELECTOR, "#problemForm button[type='submit']").click()


class ProblemDetailsPage:
    def __init__(self, driver):
        self.driver = driver

    def get_title(self):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "title"))
        ).get_attribute("value")


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
    driver.get("http://localhost:5000/")
    login_page = LoginPage(driver)
    login_page.login("test", "1234")
    # Wait for login to complete (e.g., presence of problems page)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "addProblemLink"))
    )


# --- Test Case TC014 ---

def test_add_problem_sample_code_optional_tc014(driver, login):
    driver.get("http://localhost:5000/problems")
    problems_page = ProblemsPage(driver)
    problems_page.go_to_add_problem()

    add_problem_page = AddProblemPage(driver)
    unique_title = f"Sample Optional Problem {int(time.time())}"
    add_problem_page.fill_required_fields_and_submit(
        title=unique_title,
        description="This is a test description.",
        difficulty="Easy",
        input_format="int x",
        output_format="int",
        sample_input="1",
        sample_output="2",
        constraints="1 <= x <= 100"
    )

    # Wait for redirect or success indication
    # Assume redirect to problems list or problem details page
    # Wait for either the problems list or a success message
    try:
        # Try to wait for the problems list to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "addProblemLink"))
        )
        # Optionally, check that the new problem appears in the list
        page_source = driver.page_source
        assert unique_title in page_source
    except:
        # If not redirected to problems list, check for success message
        assert "Problem added successfully" in driver.page_source

    # Ensure no validation error for missing sample code
    assert "sample code" not in driver.page_source.lower() or "required" not in driver.page_source.lower()