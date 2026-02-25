import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://localhost:5000"  # Adjust to your test environment


class ProblemDetailsPage:
    """Page Object for the Problem Details page."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # Locators
    TITLE = (By.CSS_SELECTOR, "h1.problem-title")
    DESCRIPTION = (By.CSS_SELECTOR, "div.problem-description")
    DIFFICULTY = (By.CSS_SELECTOR, "span.problem-difficulty")
    INPUT_FORMAT = (By.CSS_SELECTOR, "pre.input-format")
    OUTPUT_FORMAT = (By.CSS_SELECTOR, "pre.output-format")
    SAMPLE_INPUT = (By.CSS_SELECTOR, "pre.sample-input")
    SAMPLE_OUTPUT = (By.CSS_SELECTOR, "pre.sample-output")
    CONSTRAINTS = (By.CSS_SELECTOR, "div.problem-constraints")
    SAMPLE_CODE = (By.CSS_SELECTOR, "pre.sample-code")
    SOLVE_BUTTON = (By.CSS_SELECTOR, "button.solve-button")

    def is_element_visible(self, locator):
        try:
            self.wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def get_text(self, locator):
        try:
            element = self.wait.until(EC.visibility_of_element_located(locator))
            return element.text.strip()
        except TimeoutException:
            return ""

    def is_solve_button_visible(self):
        return self.is_element_visible(self.SOLVE_BUTTON)


@pytest.fixture(scope="session")
def driver():
    """Setup Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.set_window_size(1280, 800)
    yield driver
    driver.quit()


@pytest.fixture
def problem_details_page(driver):
    """Navigate to a sample problem details page."""
    problem_id = 1  # Replace with a valid problem ID in your test environment
    url = f"{BASE_URL}/problems/{problem_id}"
    driver.get(url)
    return ProblemDetailsPage(driver)


def test_tc009_problem_details_page_shows_all_required_information(problem_details_page):
    """
    TC009: Verify that the problem details page displays title, description, difficulty,
    input/output formats, sample input/output, constraints, sample code, and a “Solve” button.
    """

    # Verify each required element is present and visible
    assert problem_details_page.is_element_visible(
        ProblemDetailsPage.TITLE
    ), "Problem title is missing or not visible."

    assert problem_details_page.is_element_visible(
        ProblemDetailsPage.DESCRIPTION
    ), "Problem description is missing or not visible."

    assert problem_details_page.is_element_visible(
        ProblemDetailsPage.DIFFICULTY
    ), "Problem difficulty is missing or not visible."

    assert problem_details_page.is_element_visible(
        ProblemDetailsPage.INPUT_FORMAT
    ), "Input format section is missing or not visible."

    assert problem_details_page.is_element_visible(
        ProblemDetailsPage.OUTPUT_FORMAT
    ), "Output format section is missing or not visible."

    assert problem_details_page.is_element_visible(
        ProblemDetailsPage.SAMPLE_INPUT
    ), "Sample input section is missing or not visible."

    assert problem_details_page.is_element_visible(
        ProblemDetailsPage.SAMPLE_OUTPUT
    ), "Sample output section is missing or not visible."

    assert problem_details_page.is_element_visible(
        ProblemDetailsPage.CONSTRAINTS
    ), "Constraints section is missing or not visible."

    assert problem_details_page.is_element_visible(
        ProblemDetailsPage.SAMPLE_CODE
    ), "Sample code section is missing or not visible."

    # Verify the Solve button is visible
    assert problem_details_page.is_solve_button_visible(), "Solve button is not visible."

    # Optional: Verify that the text content is not empty
    assert problem_details_page.get_text(
        ProblemDetailsPage.TITLE
    ), "Problem title text is empty."

    assert problem_details_page.get_text(
        ProblemDetailsPage.DESCRIPTION
    ), "Problem description text is empty."

    assert problem_details_page.get_text(
        ProblemDetailsPage.DIFFICULTY
    ), "Problem difficulty text is empty."

    assert problem_details_page.get_text(
        ProblemDetailsPage.INPUT_FORMAT
    ), "Input format text is empty."

    assert problem_details_page.get_text(
        ProblemDetailsPage.OUTPUT_FORMAT
    ), "Output format text is empty."

    assert problem_details_page.get_text(
        ProblemDetailsPage.SAMPLE_INPUT
    ), "Sample input text is empty."

    assert problem_details_page.get_text(
        ProblemDetailsPage.SAMPLE_OUTPUT
    ), "Sample output text is empty."

    assert problem_details_page.get_text(
        ProblemDetailsPage.CONSTRAINTS
    ), "Constraints text is empty."

    assert problem_details_page.get_text(
        ProblemDetailsPage.SAMPLE_CODE
    ), "Sample code text is empty."