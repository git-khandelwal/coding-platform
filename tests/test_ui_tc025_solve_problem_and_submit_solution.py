import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions

# ---- Page Objects ----

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

    def go_to(self):
        self.driver.get(f"{self.driver.base_url}/problems")

    def open_first_problem(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".problem-link"))
        )
        self.driver.find_element(By.CSS_SELECTOR, ".problem-link").click()

class ProblemSolvePage:
    def __init__(self, driver):
        self.driver = driver

    def is_code_editor_present(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "code-editor"))
            )
            return True
        except TimeoutException:
            return False

    def enter_code(self, code):
        editor = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "code-editor"))
        )
        editor.clear()
        editor.send_keys(code)

    def submit_solution(self):
        submit_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit-solution"))
        )
        submit_btn.click()

    def wait_for_evaluation_result(self):
        try:
            result_elem = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.ID, "evaluation-result"))
            )
            return result_elem.text
        except TimeoutException:
            return None

# ---- Fixtures ----

@pytest.fixture(scope="session")
def driver():
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1280,1024")
    driver = webdriver.Chrome(options=chrome_options)
    driver.base_url = "http://localhost:5000"
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def authenticated_user(driver):
    # Precondition: user exists in DB. If not, register here.
    driver.get(driver.base_url)
    login_page = LoginPage(driver)
    login_page.login("testuser", "testpass")
    # Wait for login to complete, e.g., by checking for logout button or user dashboard
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "logout-button"))
        )
    except TimeoutException:
        # Already logged in or no logout button, proceed
        pass

# ---- Test Case TC025 ----

def test_tc025_solve_problem_and_submit_solution(driver, authenticated_user):
    # Step 2: Navigate to problems list and open a problem's solve page
    driver.get(f"{driver.base_url}/problems")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".problem-link"))
        )
    except TimeoutException:
        pytest.fail("No problems available to solve.")

    # Open the first problem
    problem_links = driver.find_elements(By.CSS_SELECTOR, ".problem-link")
    if not problem_links:
        pytest.fail("No problem links found.")
    problem_links[0].click()

    # Click the "Solve" button or navigate to solve page
    try:
        solve_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "solve-problem-btn"))
        )
        solve_btn.click()
    except TimeoutException:
        # Maybe already on solve page
        pass

    # Step 3: Enter code in editor
    problem_solve_page = ProblemSolvePage(driver)
    assert problem_solve_page.is_code_editor_present(), "Code editor is not available."

    # Example code to solve a simple problem (should match the problem requirements)
    sample_code = (
        "def solution(a, b):\n"
        "    return a + b\n"
    )
    problem_solve_page.enter_code(sample_code)

    # Step 4: Submit solution
    problem_solve_page.submit_solution()

    # Step 5: View evaluation result
    result_text = problem_solve_page.wait_for_evaluation_result()
    assert result_text is not None, "Evaluation result was not displayed."
    assert "Success" in result_text or "Correct" in result_text or "Failed" in result_text or "Error" in result_text, \
        f"Unexpected evaluation result: {result_text}"