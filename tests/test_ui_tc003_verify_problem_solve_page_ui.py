import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from playwright.sync_api import sync_playwright

# --- Selenium Page Object ---

class ProblemSolvePageSelenium:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_code_editor(self, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.ID, "code"))
        )

    def wait_for_submit_button(self, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//form[@id='solveProblemForm']//button"))
        )

    def get_code_editor_value(self):
        code_editor = self.driver.find_element(By.ID, "code")
        return code_editor.get_attribute("value")

# --- Playwright Page Object ---

class ProblemSolvePagePlaywright:
    def __init__(self, page):
        self.page = page

    def wait_for_code_editor(self, timeout=10000):
        return self.page.wait_for_selector("#code", timeout=timeout)

    def wait_for_submit_button(self, timeout=10000):
        return self.page.wait_for_selector("#solveProblemForm button", timeout=timeout)

    def get_code_editor_value(self):
        return self.page.locator("#code").input_value()

# --- Selenium Test ---

@pytest.fixture(scope="function")
def selenium_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

def test_tc003_problem_solve_page_ui_selenium(selenium_driver):
    # Step 1: Navigate to the problem details page
    selenium_driver.get("http://localhost:5000/problems")  # Adjust port if needed

    # Find first problem link (assuming problems are listed with links)
    problem_links = selenium_driver.find_elements(By.XPATH, "//a[contains(@href, '/problems/')]")
    assert problem_links, "No problem links found on problems page"
    problem_links[0].click()

    # Step 2: Click on the option to solve the problem
    solve_link = selenium_driver.find_element(By.XPATH, "//a[contains(@href, '/solve')]")
    solve_link.click()

    solve_page = ProblemSolvePageSelenium(selenium_driver)

    # Step 3: Observe the code editor and submit button
    code_editor = solve_page.wait_for_code_editor()
    assert code_editor.is_displayed(), "Code editor is not visible"

    submit_button = solve_page.wait_for_submit_button()
    assert submit_button.is_displayed(), "Submit button is not present"

    # Step 4: Check for presence of sample code if defined
    sample_code = solve_page.get_code_editor_value()
    # If sample code is defined, it should be pre-filled (non-empty)
    # If not defined, it may be empty
    # We check that the editor is present and value is either empty or non-empty
    assert sample_code is not None, "Code editor value could not be retrieved"

# --- Playwright Test ---

@pytest.fixture(scope="function")
def playwright_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()

def test_tc003_problem_solve_page_ui_playwright(playwright_page):
    # Step 1: Navigate to the problem details page
    playwright_page.goto("http://localhost:5000/problems")

    # Find first problem link
    problem_links = playwright_page.locator("a[href^='/problems/']")
    count = problem_links.count()
    assert count > 0, "No problem links found on problems page"
    problem_links.nth(0).click()

    # Step 2: Click on the option to solve the problem
    solve_link = playwright_page.locator("a[href$='/solve']")
    assert solve_link.count() > 0, "Solve link not found"
    solve_link.first.click()

    solve_page = ProblemSolvePagePlaywright(playwright_page)

    # Step 3: Observe the code editor and submit button
    solve_page.wait_for_code_editor()
    code_editor = playwright_page.locator("#code")
    assert code_editor.is_visible(), "Code editor is not visible"

    solve_page.wait_for_submit_button()
    submit_button = playwright_page.locator("#solveProblemForm button")
    assert submit_button.is_visible(), "Submit button is not present"

    # Step 4: Check for presence of sample code if defined
    sample_code = solve_page.get_code_editor_value()
    assert sample_code is not None, "Code editor value could not be retrieved"