import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PROBLEMS_LIST_URL = "http://localhost:5000/problems"  # Adjust as needed

class ProblemsListPage:
    PROBLEM_TITLE_LINKS = (By.CSS_SELECTOR, "table.problems-table tbody tr td a.problem-link")
    TABLE_ROWS = (By.CSS_SELECTOR, "table.problems-table tbody tr")

    def __init__(self, driver):
        self.driver = driver

    def wait_for_page(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.TABLE_ROWS)
        )

    def get_problem_title_elements(self):
        return self.driver.find_elements(*self.PROBLEM_TITLE_LINKS)

    def get_problem_titles(self):
        return [el.text.strip() for el in self.get_problem_title_elements()]

@pytest.fixture(scope="function")
def driver():
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(2)
    yield driver
    driver.quit()

def test_tc009_problems_list_titles_displayed(driver):
    # Step 1: Navigate to the problems list page
    driver.get(PROBLEMS_LIST_URL)
    problems_page = ProblemsListPage(driver)
    problems_page.wait_for_page()

    # Step 2: Observe the list items (table rows)
    title_elements = problems_page.get_problem_title_elements()
    assert title_elements, "No problems found in the problems list (at least one expected)."

    # Expected Result: Each problem entry displays a title
    for idx, title_el in enumerate(title_elements, start=1):
        title_text = title_el.text.strip()
        assert title_text, f"Problem at row {idx} does not display a title."