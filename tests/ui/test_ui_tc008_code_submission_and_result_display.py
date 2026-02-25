import re
import json
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from playwright.sync_api import sync_playwright, Playwright, Request, Route

# ------------------------------
# Page Object Models
# ------------------------------

class LoginPage:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.username_input = (By.ID, "login-username")
        self.password_input = (By.ID, "login-password")
        self.submit_button = (By.XPATH, "//form[@id='login-form']//button[@type='submit']")

    def login(self, username: str, password: str):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.username_input)
        )
        self.driver.find_element(*self.username_input).clear()
        self.driver.find_element(*self.username_input).send_keys(username)
        self.driver.find_element(*self.password_input).clear()
        self.driver.find_element(*self.password_input).send_keys(password)
        self.driver.find_element(*self.submit_button).click()
        # Wait for login to complete, e.g., by checking presence of protected button
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "protected-button"))
        )

class ProblemSolvePage:
    def __init__(self, driver: webdriver.Chrome, problem_id: int):
        self.driver = driver
        self.problem_id = problem_id
        self.url = f"/problems/{problem_id}/solve"
        self.editor = (By.CSS_SELECTOR, ".editor")  # placeholder selector
        self.submit_button = (By.ID, "submit-code")
        self.result_panel = (By.ID, "result-panel")
        self.status_text = (By.ID, "result-status")
        self.result_text = (By.ID, "result-output")
        self.user_print = (By.ID, "user-print")

    def navigate(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.editor)
        )

    def write_code(self, code: str):
        editor_elem = self.driver.find_element(*self.editor)
        # Clear existing content
        editor_elem.clear()
        editor_elem.send_keys(code)

    def submit(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.submit_button)
        )
        self.driver.find_element(*self.submit_button).click()

    def wait_for_result(self):
        WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located(self.result_panel)
        )

    def get_result(self):
        status = self.driver.find_element(*self.status_text).text.strip()
        result = self.driver.find_element(*self.result_text).text.strip()
        user_print = self.driver.find_element(*self.user_print).text.strip()
        return status, result, user_print

# ------------------------------
# Fixtures
# ------------------------------

@pytest.fixture(scope="session")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)
    yield driver
    driver.quit()

@pytest.fixture(scope="session")
def playwright_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        yield context
        context.close()
        browser.close()

@pytest.fixture
def login(driver):
    login_page = LoginPage(driver)
    login_page.login("fortnite", "fortnite")

@pytest.fixture
def problem_id(driver):
    # Navigate to problems list and click first problem card
    driver.get("/problems")
    # Assume each problem card has a link with class 'problem-card'
    card_locator = (By.CSS_SELECTOR, ".problem-card")
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(card_locator)
    )
    first_card = driver.find_element(*card_locator)
    href = first_card.get_attribute("href")
    # Extract numeric ID from URL
    match = re.search(r"/problems/(\d+)/", href)
    if not match:
        raise ValueError("Could not extract problem ID from href")
    return int(match.group(1))

# ------------------------------
# Helper Functions
# ------------------------------

def fetch_problem_details(context: Playwright, problem_id: int):
    """
    Uses Playwright's request API to fetch problem details.
    Assumes an API endpoint exists at /api/problems/<id>.
    """
    response = context.request.get(f"http://localhost:5000/api/problems/{problem_id}")
    if not response.ok:
        raise RuntimeError(f"Failed to fetch problem details: {response.status}")
    return response.json()

def generate_solution_code(sample_input: str, sample_output: str):
    """
    Generates a minimal Python function that returns the expected output.
    This is a naive implementation that simply returns the sample output.
    """
    # Attempt to parse sample_output as a Python literal
    try:
        parsed_output = json.loads(sample_output)
    except Exception:
        parsed_output = sample_output.strip('"\'')
    # Escape quotes in output
    if isinstance(parsed_output, str):
        parsed_output = parsed_output.replace('"', '\\"')
        return f'def solution():\n    print("{parsed_output}")'
    else:
        return f'def solution():\n    return {parsed_output}'

# ------------------------------
# Test Case TC008
# ------------------------------

def test_tc008(driver, playwright_context, login, problem_id):
    """
    TC008: Code submission and result display
    """
    # Fetch problem details using Playwright
    problem_details = fetch_problem_details(playwright_context, problem_id)
    sample_input = problem_details.get("sample_input", "")
    sample_output = problem_details.get("sample_output", "")

    # Generate code that should produce the correct result
    code_snippet = generate_solution_code(sample_input, sample_output)

    # Initialize page object for the solve page
    solve_page = ProblemSolvePage(driver, problem_id)
    solve_page.navigate()

    # Write code into the editor
    try: