import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

    def wait_for_problems_list(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "problemsList"))
        )

    def get_problems(self):
        self.wait_for_problems_list()
        problems_list = self.driver.find_element(By.ID, "problemsList")
        return problems_list.find_elements(By.TAG_NAME, "li")

    def get_problem_data(self):
        problems = self.get_problems()
        problem_data = []
        for li in problems:
            # Title is in <a class="problem-link">, difficulty is likely in a span or text
            title_elem = li.find_element(By.CLASS_NAME, "problem-link")
            title = title_elem.text
            # Try to find the difficulty in the li (could be in a span, or as text)
            difficulty = ""
            try:
                # Look for a span with class 'difficulty' if present
                difficulty_elem = li.find_element(By.CLASS_NAME, "difficulty")
                difficulty = difficulty_elem.text
            except Exception:
                # Fallback: get all text and subtract title
                text = li.text
                difficulty = text.replace(title, "").strip()
            problem_data.append({"title": title, "difficulty": difficulty})
        return problem_data

# --- Fixtures and Setup/Teardown ---

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

# --- Test Data Utility (for expected problems) ---

def get_expected_problems():
    # This should be replaced with a DB fixture, API call, or static data as appropriate.
    # For demonstration, we use static sample data.
    return [
        {"title": "Two Sum", "difficulty": "Easy"},
        {"title": "Reverse Linked List", "difficulty": "Medium"},
        {"title": "Word Ladder", "difficulty": "Hard"},
    ]

# --- Test Case Implementation ---

def test_TC001_problems_list_display(driver):
    base_url = "http://localhost:5000"
    driver.get(f"{base_url}/")
    # If login is required, perform login
    try:
        login_form = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "login-form"))
        )
        login_page = LoginPage(driver)
        login_page.login("test", "1234")
        # Wait for redirect after login
        WebDriverWait(driver, 5).until(EC.url_changes(f"{base_url}/"))
    except Exception:
        # Login not required or already logged in
        pass

    # Navigate to problems list page
    driver.get(f"{base_url}/problems")
    problems_page = ProblemsListPage(driver)
    problems_page.wait_for_problems_list()

    # Get displayed problems
    displayed_problems = problems_page.get_problem_data()

    # Get expected problems (replace with real data source in production)
    expected_problems = get_expected_problems()

    # Assert that all expected problems are present and no extra
    displayed_titles = sorted([(p["title"], p["difficulty"]) for p in displayed_problems])
    expected_titles = sorted([(p["title"], p["difficulty"]) for p in expected_problems])

    assert displayed_titles == expected_titles, (
        f"Displayed problems do not match expected.\n"
        f"Expected: {expected_titles}\n"
        f"Found: {displayed_titles}"
    )