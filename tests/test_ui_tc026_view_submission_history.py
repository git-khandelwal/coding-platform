import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Constants (adjust as needed)
BASE_URL = "http://localhost:5000"
USERNAME = "testuser_tc026"
PASSWORD = "TestPass123!"
PROBLEM_TITLE = "Sample Problem TC026"
PROBLEM_DESC = "Sample description for TC026"
PROBLEM_DIFFICULTY = "Easy"
PROBLEM_INPUT_FORMAT = "Input"
PROBLEM_OUTPUT_FORMAT = "Output"
PROBLEM_SAMPLE_INPUT = "1"
PROBLEM_SAMPLE_OUTPUT = "2"
PROBLEM_SAMPLE_CODE = "def add(a, b):\n    return a + b"
PROBLEM_CONSTRAINTS = "a, b > 0"
SOLUTION_CODE = "def add(a, b):\n    return a + b"

@pytest.fixture(scope="class")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

class IndexPage:
    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(BASE_URL)

    def register(self, username, password):
        self.driver.find_element(By.ID, "register-username").clear()
        self.driver.find_element(By.ID, "register-username").send_keys(username)
        self.driver.find_element(By.ID, "register-password").clear()
        self.driver.find_element(By.ID, "register-password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "#register-form button[type='submit']").click()

    def login(self, username, password):
        self.driver.find_element(By.ID, "login-username").clear()
        self.driver.find_element(By.ID, "login-username").send_keys(username)
        self.driver.find_element(By.ID, "login-password").clear()
        self.driver.find_element(By.ID, "login-password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "#login-form button[type='submit']").click()

class ProblemsPage:
    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(f"{BASE_URL}/problems")

    def click_add_problem(self):
        add_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Add Problem"))
        )
        add_link.click()

    def open_problem_by_title(self, title):
        problem_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, title))
        )
        problem_link.click()

class AddProblemPage:
    def __init__(self, driver):
        self.driver = driver

    def submit_problem(self, title, desc, difficulty, input_format, output_format, sample_input, sample_output, sample_code, constraints):
        self.driver.find_element(By.NAME, "title").send_keys(title)
        self.driver.find_element(By.NAME, "description").send_keys(desc)
        self.driver.find_element(By.NAME, "difficulty").send_keys(difficulty)
        self.driver.find_element(By.NAME, "input_format").send_keys(input_format)
        self.driver.find_element(By.NAME, "output_format").send_keys(output_format)
        self.driver.find_element(By.NAME, "sample_input").send_keys(sample_input)
        self.driver.find_element(By.NAME, "sample_output").send_keys(sample_output)
        self.driver.find_element(By.NAME, "sample_code").send_keys(sample_code)
        self.driver.find_element(By.NAME, "constraints").send_keys(constraints)
        self.driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()

class ProblemDetailsPage:
    def __init__(self, driver):
        self.driver = driver

    def click_solve(self):
        solve_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Solve"))
        )
        solve_link.click()

class ProblemSolvePage:
    def __init__(self, driver):
        self.driver = driver

    def submit_solution(self, code):
        code_editor = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "code"))
        )
        code_editor.clear()
        code_editor.send_keys(code)
        self.driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()

    def wait_for_submission_result(self):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".submission-result"))
        )

    def go_to_submission_history(self):
        history_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Submission History"))
        )
        history_link.click()

class SubmissionHistoryPage:
    def __init__(self, driver):
        self.driver = driver

    def get_latest_submission(self):
        table = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "submission-history-table"))
        )
        rows = table.find_elements(By.TAG_NAME, "tr")
        if len(rows) < 2:
            return None
        return rows[1].text

@pytest.mark.usefixtures("driver")
class TestViewSubmissionHistoryTC026:
    def test_view_submission_history_tc026(self, driver):
        # Step 1: Register and log in as user
        index = IndexPage(driver)
        index.open()
        # Try registering, ignore if user exists
        try:
            index.register(USERNAME, PASSWORD)
            WebDriverWait(driver, 2).until(
                EC.alert_is_present()
            )
            driver.switch_to.alert.accept()
        except Exception:
            pass
        index.login(USERNAME, PASSWORD)
        # Wait for login to complete (e.g., by checking for problems link)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Problems"))
        )

        # Step 2: Navigate to problem solve page (create problem if needed)
        problems = ProblemsPage(driver)
        problems.open()
        # Check if problem exists, else add it
        try:
            problems.open_problem_by_title(PROBLEM_TITLE)
        except Exception:
            problems.click_add_problem()
            add_problem = AddProblemPage(driver)
            add_problem.submit_problem(
                PROBLEM_TITLE,
                PROBLEM_DESC,
                PROBLEM_DIFFICULTY,
                PROBLEM_INPUT_FORMAT,
                PROBLEM_OUTPUT_FORMAT,
                PROBLEM_SAMPLE_INPUT,
                PROBLEM_SAMPLE_OUTPUT,
                PROBLEM_SAMPLE_CODE,
                PROBLEM_CONSTRAINTS
            )
            # After submit, go back to problems list and open problem
            problems.open()
            problems.open_problem_by_title(PROBLEM_TITLE)

        # Now on problem details page, click Solve
        details = ProblemDetailsPage(driver)
        details.click_solve()

        # Step 3: Submit a solution
        solve = ProblemSolvePage(driver)
        solve.submit_solution(SOLUTION_CODE)
        # Wait for submission result
        solve.wait_for_submission_result()

        # Step 4: View submission history section
        solve.go_to_submission_history()
        history = SubmissionHistoryPage(driver)
        latest = history.get_latest_submission()

        # Assert latest submission is present and contains expected code or status
        assert latest is not None, "No submission found in history"
        assert "add(a, b)" in latest or "Success" in latest or "Correct" in latest, "Latest submission not found or incorrect in history"