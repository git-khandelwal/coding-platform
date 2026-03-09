import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Page Object for Problem Details Page ---

class ProblemDetailsPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def wait_for_page_to_load(self):
        # Wait for the title to be present as a proxy for page load
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-testid="problem-title"], h1, h2')))

    def is_title_visible(self):
        return self._is_any_visible([
            (By.CSS_SELECTOR, '[data-testid="problem-title"]'),
            (By.TAG_NAME, 'h1'),
            (By.TAG_NAME, 'h2')
        ])

    def is_description_visible(self):
        return self._is_any_visible([
            (By.CSS_SELECTOR, '[data-testid="problem-description"]'),
            (By.XPATH, "//*[contains(text(), 'Description')]/following-sibling::*"),
            (By.XPATH, "//div[contains(@class, 'description')]")
        ])

    def is_difficulty_visible(self):
        return self._is_any_visible([
            (By.CSS_SELECTOR, '[data-testid="problem-difficulty"]'),
            (By.XPATH, "//*[contains(text(), 'Difficulty')]/following-sibling::*"),
            (By.XPATH, "//div[contains(@class, 'difficulty')]")
        ])

    def is_input_format_visible(self):
        return self._is_any_visible([
            (By.CSS_SELECTOR, '[data-testid="problem-input-format"]'),
            (By.XPATH, "//*[contains(text(), 'Input Format') or contains(text(), 'Input')]/following-sibling::*"),
            (By.XPATH, "//div[contains(@class, 'input-format')]")
        ])

    def is_output_format_visible(self):
        return self._is_any_visible([
            (By.CSS_SELECTOR, '[data-testid="problem-output-format"]'),
            (By.XPATH, "//*[contains(text(), 'Output Format') or contains(text(), 'Output')]/following-sibling::*"),
            (By.XPATH, "//div[contains(@class, 'output-format')]")
        ])

    def is_sample_input_visible(self):
        return self._is_any_visible([
            (By.CSS_SELECTOR, '[data-testid="problem-sample-input"]'),
            (By.XPATH, "//*[contains(text(), 'Sample Input')]/following-sibling::*"),
            (By.XPATH, "//div[contains(@class, 'sample-input')]")
        ])

    def is_sample_output_visible(self):
        return self._is_any_visible([
            (By.CSS_SELECTOR, '[data-testid="problem-sample-output"]'),
            (By.XPATH, "//*[contains(text(), 'Sample Output')]/following-sibling::*"),
            (By.XPATH, "//div[contains(@class, 'sample-output')]")
        ])

    def is_constraints_visible(self):
        return self._is_any_visible([
            (By.CSS_SELECTOR, '[data-testid="problem-constraints"]'),
            (By.XPATH, "//*[contains(text(), 'Constraint')]/following-sibling::*"),
            (By.XPATH, "//div[contains(@class, 'constraints')]")
        ])

    def _is_any_visible(self, locators):
        for by, value in locators:
            try:
                element = self.wait.until(EC.visibility_of_element_located((by, value)))
                if element.is_displayed():
                    return True
            except Exception:
                continue
        return False

# --- Fixtures ---

@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(2)
    yield driver
    driver.quit()

@pytest.fixture
def problem_details_page(driver):
    # Precondition: At least one problem exists.
    # Step 1: Go to the problems list page and get the first problem's details link.
    driver.get("http://localhost:5000/problems")
    try:
        # Try to find the first problem's link (assume <a href="/problems/{id}"> or data-testid)
        problem_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'ul#problemsList li a[href^="/problems/"], a[href^="/problems/"]'
            ))
        )
    except Exception:
        pytest.skip("No problems found in the problems list page.")
    problem_url = problem_link.get_attribute("href")
    # Step 2: Navigate to the problem details page
    driver.get(problem_url)
    page = ProblemDetailsPage(driver)
    page.wait_for_page_to_load()
    return page

# --- Test Case TC010 ---

def test_problem_details_page_content_display_tc010(problem_details_page):
    """
    TC010: Problem Details Page - Content Display
    Verify that the problem details page displays all required information.
    """
    assert problem_details_page.is_title_visible(), "Problem title is not visible"
    assert problem_details_page.is_description_visible(), "Problem description is not visible"
    assert problem_details_page.is_difficulty_visible(), "Problem difficulty is not visible"
    assert problem_details_page.is_input_format_visible(), "Problem input format is not visible"
    assert problem_details_page.is_output_format_visible(), "Problem output format is not visible"
    assert problem_details_page.is_sample_input_visible(), "Problem sample input is not visible"
    assert problem_details_page.is_sample_output_visible(), "Problem sample output is not visible"
    assert problem_details_page.is_constraints_visible(), "Problem constraints are not visible"