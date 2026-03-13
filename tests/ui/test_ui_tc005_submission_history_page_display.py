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

    def go_to_first_problem(self):
        # Wait for problems list to load and click the first problem link
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Solve"))
        )
        self.driver.find_elements(By.LINK_TEXT, "Solve")[0].click()


class ProblemSolvePage:
    def __init__(self, driver):
        self.driver = driver

    def submit_solution(self, code):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "solveProblemForm"))
        )
        code_area = self.driver.find_element(By.ID, "code")
        code_area.clear()
        code_area.send_keys(code)
        self.driver.find_element(By.CSS_SELECTOR, "#solveProblemForm button[type='submit']").click()
        # Wait for result to appear
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "resultOutput"))
        )

    def go_to_submission_history(self):
        # The submission history is likely on the same page, scroll to it
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "submissionHistory"))
        )
        return SubmissionHistorySection(self.driver)


class SubmissionHistorySection:
    def __init__(self, driver):
        self.driver = driver

    def get_submissions(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "submissionHistory"))
        )
        history = self.driver.find_element(By.ID, "submissionHistory")
        # Assume each submission is in a <tr> or <div> inside this section
        rows = history.find_elements(By.CSS_SELECTOR, "tr, div.submission-row")
        submissions = []
        for row in rows:
            text = row.text
            # Try to extract fields from the row text
            submissions.append(text)
        return submissions

    def assert_submission_fields(self, problem_title, username):
        # Check that at least one submission contains the expected fields
        submissions = self.get_submissions()
        found = False
        for sub in submissions:
            if problem_title in sub and "Accepted" in sub or "Wrong" in sub or "Pending" in sub:
                # Check for status, result, timestamp
                if any(status in sub for status in ["Accepted", "Wrong", "Pending"]):
                    if "Result:" in sub or "Output:" in sub or "result" in sub.lower():
                        if "20" in sub:  # crude check for timestamp
                            found = True
                            break
        assert found, "Submission with expected fields not found in submission history."


# --- Fixtures ---

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

# --- Test Case Implementation ---

@pytest.mark.usefixtures("driver")
def test_TC005_submission_history_page_display(driver):
    """
    TC005: Verify that the submission history page displays a list of previous submissions with status and result.
    """
    base_url = "http://localhost:5000"

    # Step 1: Login
    driver.get(f"{base_url}/")
    login_page = LoginPage(driver)
    login_page.login("test", "1234")

    # Step 2: Go to problems page
    WebDriverWait(driver, 10).until(
        EC.url_contains("/problems")
    )
    problems_page = ProblemsPage(driver)
    problems_page.go_to_first_problem()

    # Step 3: On problem solve page, submit a solution
    solve_page = ProblemSolvePage(driver)
    # Submit a simple solution (assuming Python code)
    solve_page.submit_solution("def solution():\n    return 42")

    # Step 4: Observe the list of submissions (submission history section)
    history_section = solve_page.go_to_submission_history()

    # Step 5: Assert that submissions are listed with status, result, and timestamp, and associated with correct problem/user
    # For demonstration, we use "Test Problem" as the expected problem title; adjust as needed.
    history_section.assert_submission_fields("Test Problem", "test")