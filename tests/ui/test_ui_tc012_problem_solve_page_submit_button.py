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
        self.submit_button = (By.XPATH, "//form[@id='login-form']//button")

    def login(self, username, password):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.username_input)
        ).send_keys(username)
        self.driver.find_element(*self.password_input).send_keys(password)
        self.driver.find_element(*self.submit_button).click()


class ProblemSolvePage:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_page(self):
        # Wait for the code textarea as an anchor for page load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "code"))
        )

    def get_submit_button(self):
        # Try to find a button with text 'Submit' or a type submit inside the form
        try:
            # Prefer button with visible text 'Submit'
            return WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//form[@id='solveProblemForm']//button[normalize-space(text())='Submit']")
                )
            )
        except:
            # Fallback: any submit button in the form
            return WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//form[@id='solveProblemForm']//button[@type='submit']")
                )
            )

# --- Fixtures ---

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def authenticated_driver(driver):
    driver.get("http://localhost:5000/")
    login_page = LoginPage(driver)
    login_page.login("test", "1234")
    # Wait for login to complete (e.g., presence of protected content or redirect)
    WebDriverWait(driver, 10).until(
        EC.url_contains("/problems")
    )
    return driver

@pytest.fixture(scope="function")
def problem_id(authenticated_driver):
    # Find a problem to solve (assume at least one exists)
    driver = authenticated_driver
    driver.get("http://localhost:5000/problems")
    # Find the first problem link (assuming links to /problems/<id>)
    problem_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[contains(@href, '/problems/') and contains(@href, '/solve')] | //a[contains(@href, '/problems/')]")
        )
    )
    href = problem_link.get_attribute("href")
    # Extract the problem ID
    import re
    match = re.search(r'/problems/(\d+)', href)
    assert match, "No problem link found"
    return match.group(1)

# --- Test Case ---

def test_TC012_problem_solve_page_has_submit_button(authenticated_driver, problem_id):
    """
    TC012: Verify that the problem solve page contains a submit button for code submission.
    """
    driver = authenticated_driver
    solve_url = f"http://localhost:5000/problems/{problem_id}/solve"
    driver.get(solve_url)
    page = ProblemSolvePage(driver)
    page.wait_for_page()

    submit_button = page.get_submit_button()
    assert submit_button is not None, "Submit button not found on the problem solve page"
    assert submit_button.is_enabled(), "Submit button is present but not enabled"
    # Check button label is clearly 'Submit'
    label = submit_button.text.strip().lower()
    assert "submit" in label, f"Submit button label is not clear: '{submit_button.text}'"