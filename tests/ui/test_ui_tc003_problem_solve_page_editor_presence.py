import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LOGIN_URL = "http://localhost:5000/"
PROBLEMS_URL = "http://localhost:5000/problems"
PROBLEM_SOLVE_URL_TEMPLATE = "http://localhost:5000/problems/{problem_id}/solve"

USERNAME = "test"
PASSWORD = "1234"

@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    def login(self, username, password):
        self.driver.get(LOGIN_URL)
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

    def select_first_problem(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        table = self.driver.find_element(By.TAG_NAME, "table")
        first_row = table.find_elements(By.TAG_NAME, "tr")[1]  # skip header
        first_link = first_row.find_element(By.TAG_NAME, "a")
        first_link.click()

    def get_first_problem_id(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        table = self.driver.find_element(By.TAG_NAME, "table")
        first_row = table.find_elements(By.TAG_NAME, "tr")[1]  # skip header
        first_link = first_row.find_element(By.TAG_NAME, "a")
        href = first_link.get_attribute("href")
        # href example: http://localhost:5000/problems/1
        problem_id = href.rstrip('/').split('/')[-1]
        return problem_id

class ProblemDetailsPage:
    def __init__(self, driver):
        self.driver = driver

    def click_solve_button(self):
        # Try to find a button or link to solve the problem
        try:
            solve_button = self.driver.find_element(By.LINK_TEXT, "Solve")
            solve_button.click()
        except:
            # Fallback: try a button with id or a form
            try:
                solve_button = self.driver.find_element(By.ID, "solveProblemButton")
                solve_button.click()
            except:
                raise Exception("Solve button not found on problem details page.")

class ProblemSolvePage:
    def __init__(self, driver):
        self.driver = driver

    def is_code_editor_present_and_enabled(self):
        code_area = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "code"))
        )
        assert code_area.is_displayed(), "Code editor is not visible"
        assert code_area.is_enabled(), "Code editor is not enabled"
        readonly = code_area.get_attribute("readonly")
        assert not readonly, "Code editor is read-only"
        return True

@pytest.mark.usefixtures("driver")
def test_TC003_problem_solve_page_editor_presence(driver):
    # Login
    login_page = LoginPage(driver)
    login_page.login(USERNAME, PASSWORD)

    # Go to problems listing
    driver.get(PROBLEMS_URL)
    problems_page = ProblemsPage(driver)
    problem_id = problems_page.get_first_problem_id()

    # Go directly to the solve page for the first problem
    solve_url = PROBLEM_SOLVE_URL_TEMPLATE.format(problem_id=problem_id)
    driver.get(solve_url)

    # Verify code editor presence and enabled state
    solve_page = ProblemSolvePage(driver)
    assert solve_page.is_code_editor_present_and_enabled()