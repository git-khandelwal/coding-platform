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
            EC.presence_of_element_located(self.username_input)
        )
        self.driver.find_element(*self.username_input).clear()
        self.driver.find_element(*self.username_input).send_keys(username)
        self.driver.find_element(*self.password_input).clear()
        self.driver.find_element(*self.password_input).send_keys(password)
        self.driver.find_element(*self.login_form).submit()

class ProblemsListPage:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_page(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "addProblemLink"))
        )

    def click_first_problem_title(self):
        # Try to find the first problem title link (robust selector: look for a table/list with links)
        # We'll use the first <a> inside the main content area after addProblemLink
        add_problem_link = self.driver.find_element(By.ID, "addProblemLink")
        # Find the first <a> after addProblemLink
        problem_links = self.driver.find_elements(By.XPATH, "//a[not(@id='addProblemLink')]")
        if not problem_links:
            raise Exception("No problem links found on the problems list page.")
        problem_links[0].click()

class ProblemDetailsPage:
    def __init__(self, driver):
        self.driver = driver
        self.description = (By.ID, "description")
        self.problem_id = (By.ID, "problemId")

    def wait_for_page(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.description)
        )

    def get_problem_description(self):
        return self.driver.find_element(*self.description).text

    def is_loaded(self):
        try:
            self.wait_for_page()
            return True
        except Exception:
            return False

# --- Pytest Fixtures ---

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

# --- Test Case TC010 ---

def test_tc010_problem_list_navigation_to_details(driver):
    base_url = "http://localhost:5000"
    driver.get(f"{base_url}/")

    # Login
    login_page = LoginPage(driver)
    login_page.login("test", "1234")

    # Navigate to problems list page
    driver.get(f"{base_url}/problems")
    problems_list_page = ProblemsListPage(driver)
    problems_list_page.wait_for_page()

    # Click on a problem title
    problems_list_page.click_first_problem_title()

    # Observe navigation and verify details page
    problem_details_page = ProblemDetailsPage(driver)
    assert problem_details_page.is_loaded(), "Problem details page did not load."

    description_text = problem_details_page.get_problem_description()
    assert description_text.strip() != "", "Problem description should not be empty."