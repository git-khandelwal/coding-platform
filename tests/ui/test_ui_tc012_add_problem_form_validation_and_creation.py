import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException
from playwright.sync_api import sync_playwright, Page
import time

BASE_URL = "http://localhost:5000"

# -------------------- Selenium Page Objects -------------------- #
class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def login(self, username: str, password: str):
        self.wait.until(EC.visibility_of_element_located((By.ID, "login-username"))).send_keys(username)
        self.driver.find_element(By.ID, "login-password").send_keys(password)
        self.driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()
        # Wait for login to complete (e.g., presence of protected button)
        self.wait.until(EC.visibility_of_element_located((By.ID, "protected-button")))


class AddProblemPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def fill_problem(self, data: dict):
        self.wait.until(EC.visibility_of_element_located((By.ID, "title"))).send_keys(data["title"])
        self.driver.find_element(By.ID, "description").send_keys(data["description"])
        self.driver.find_element(By.ID, "difficulty").send_keys(data["difficulty"])
        self.driver.find_element(By.ID, "input_format").send_keys(data["input_format"])
        self.driver.find_element(By.ID, "output_format").send_keys(data["output_format"])
        self.driver.find_element(By.ID, "sample_input").send_keys(data["sample_input"])
        self.driver.find_element(By.ID, "sample_output").send_keys(data["sample_output"])
        self.driver.find_element(By.ID, "constraints").send_keys(data["constraints"])

    def submit(self):
        self.driver.find_element(By.XPATH, "//button[contains(text(),'Submit')]").click()
        # Wait for success message
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Problem added successfully')]")))


# -------------------- Fixtures -------------------- #
@pytest.fixture(scope="session")
def driver():
    # Choose Chrome; fallback to Firefox if Chrome not available
    try:
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        service = ChromeService()
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception:
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")
        service = FirefoxService()
        driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.implicitly_wait(5)
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


# -------------------- Test Case -------------------- #
def test_tc012_add_problem_success(driver, playwright_context):
    """
    TC012: Add problem form validation and creation
    """
    # 1. Log in as an authenticated user
    driver.get(f"{BASE_URL}/")
    login_page = LoginPage(driver)
    login_page.login(username="admin_user", password="securePass123")

    # 2. Navigate to the “Add Problem” page
    driver.get(f"{BASE_URL}/problems/add")
    add_problem_page = AddProblemPage(driver)

    # 3. Fill in all required fields
    problem_data = {
        "title": f"Test Problem {int(time.time())}",
        "description": "This is a test problem description.",
        "difficulty": "Easy",
        "input_format": "First line contains an integer N.",
        "output_format": "Print the sum of first N natural numbers.",
        "sample_input": "5",
        "sample_output": "15",
        "constraints": "1 <= N <= 1000"
    }
    add_problem_page.fill_problem(problem_data)

    # 4. Click the “Submit” button
    add_problem_page.submit()

    # 5. Verify success message appears (already waited in submit)

    # 6. Verify the new problem appears in the problems list using Playwright
    page: Page = playwright_context.new_page()
    page.goto(f"{BASE_URL}/problems")
    # Wait for the list to load
    page.wait_for_selector("div.problem-card", timeout=10000)
    # Retrieve all problem titles
    titles = page.locator("div.problem-card h3").all_text_contents()
    assert problem_data["title"] in titles, f"Problem title '{problem_data['title']}' not found in problems list"

    page.close()