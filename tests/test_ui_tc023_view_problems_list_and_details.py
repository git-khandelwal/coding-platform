import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PROBLEMS_LIST_URL = "http://localhost:5000/problems"

class ProblemsListPage:
    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(PROBLEMS_LIST_URL)

    def wait_for_problems_list(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.ID, "problemsList"))
        )

    def get_problem_links(self):
        self.wait_for_problems_list()
        return self.driver.find_elements(By.CSS_SELECTOR, "#problemsList li a")

    def click_first_problem(self):
        links = self.get_problem_links()
        if not links:
            raise Exception("No problems found in the list.")
        links[0].click()

class ProblemDetailsPage:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_problem_details(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1, h2"))
        )

    def get_problem_title(self):
        self.wait_for_problem_details()
        # Try h1 first, then h2
        try:
            return self.driver.find_element(By.TAG_NAME, "h1").text
        except:
            return self.driver.find_element(By.TAG_NAME, "h2").text

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1280, 1024)
    yield driver
    driver.quit()

def test_tc023_view_problems_list_and_details(driver):
    # Step 1: Navigate to problems list page
    problems_list_page = ProblemsListPage(driver)
    problems_list_page.open()

    # Step 2: View list of problems
    problems_list_page.wait_for_problems_list()
    problem_links = problems_list_page.get_problem_links()
    assert len(problem_links) > 0, "Problems list is empty, but at least one problem should exist."

    first_problem_title = problem_links[0].text
    assert first_problem_title.strip() != "", "First problem link has no title."

    # Step 3: Click on a problem to view details
    problems_list_page.click_first_problem()

    # Step 4: Verify problem details are shown
    problem_details_page = ProblemDetailsPage(driver)
    problem_details_page.wait_for_problem_details()
    details_title = problem_details_page.get_problem_title()
    assert details_title.strip() != "", "Problem details page does not show a title."
    # Optionally, check that the title matches the one from the list
    assert first_problem_title.strip() in details_title.strip(), "Problem details title does not match the selected problem."