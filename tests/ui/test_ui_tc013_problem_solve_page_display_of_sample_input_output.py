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

    def login(self, username, password):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.username_input)
        ).send_keys(username)
        self.driver.find_element(*self.password_input).send_keys(password)
        self.driver.find_element(*self.login_form).submit()


class ProblemsPage:
    def __init__(self, driver):
        self.driver = driver

    def open_first_problem(self):
        # Wait for the problems table/list to appear and click the first problem link
        # We assume that the problem links are in <a> tags with href like '/problems/<id>'
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "/problems/"))
        )
        problem_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/problems/')]")
        assert problem_links, "No problem links found on the problems page"
        problem_links[0].click()


class ProblemSolvePage:
    def __init__(self, driver):
        self.driver = driver
        # The sample input/output may be in elements with id="sample_input" and id="sample_output"
        self.sample_input = (By.ID, "sample_input")
        self.sample_output = (By.ID, "sample_output")

    def get_sample_input_text(self):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.sample_input)
        ).text

    def get_sample_output_text(self):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.sample_output)
        ).text

    def sample_input_is_visible(self):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.sample_input)
        )

    def sample_output_is_visible(self):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.sample_output)
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


# --- Test Case Implementation ---

@pytest.mark.usefixtures("driver")
def test_TC013_problem_solve_page_displays_sample_input_output(driver):
    """
    TC013: Verify that the sample input and output are displayed on the problem solve page for reference.
    """

    BASE_URL = "http://localhost:5000"  # Change as appropriate for your environment

    # Step 1: Login
    driver.get(f"{BASE_URL}/")
    login_page = LoginPage(driver)
    login_page.login("test", "1234")

    # Step 2: Navigate to /problems
    driver.get(f"{BASE_URL}/problems")
    problems_page = ProblemsPage(driver)
    problems_page.open_first_problem()

    # Step 3: On problem details, click "Solve" or navigate to solve page
    # Try to find a "Solve" button or link, otherwise go to /problems/<id>/solve
    current_url = driver.current_url
    if "/problems/" in current_url:
        problem_id = current_url.rstrip('/').split('/')[-1]
        driver.get(f"{BASE_URL}/problems/{problem_id}/solve")
    else:
        pytest.fail("Could not determine problem ID from URL.")

    # Step 4: Observe sample input/output
    solve_page = ProblemSolvePage(driver)

    # Wait for sample input/output to be visible
    assert solve_page.sample_input_is_visible(), "Sample input is not visible on the problem solve page"
    assert solve_page.sample_output_is_visible(), "Sample output is not visible on the problem solve page"

    sample_input_text = solve_page.get_sample_input_text()
    sample_output_text = solve_page.get_sample_output_text()

    # Basic content check: not empty
    assert sample_input_text.strip() != "", "Sample input is empty"
    assert sample_output_text.strip() != "", "Sample output is empty"

    # Optionally, if you know the expected content, you can check for it here
    # For now, we just check that the elements are present and not empty