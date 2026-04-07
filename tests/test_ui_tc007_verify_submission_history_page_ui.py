import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from playwright.sync_api import sync_playwright

# --- Selenium Page Objects ---

class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    def login(self, username, password):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login-form"))
        )
        self.driver.find_element(By.ID, "login-username").send_keys(username)
        self.driver.find_element(By.ID, "login-password").send_keys(password)
        self.driver.find_element(By.ID, "login-form").submit()

class SubmissionHistoryPage:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_table(self):
        # Assume table has id 'submissionHistory' based on code context
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "submissionHistory"))
        )

    def get_table_rows(self):
        table = self.driver.find_element(By.ID, "submissionHistory")
        return table.find_elements(By.TAG_NAME, "tr")

    def get_table_columns(self, row):
        return row.find_elements(By.TAG_NAME, "td")

# --- Selenium Fixtures and Test ---

@pytest.fixture(scope="function")
def selenium_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

@pytest.mark.tc007
def test_tc007_submission_history_ui_selenium(selenium_driver):
    # Step 1: Log in as a user
    selenium_driver.get("http://localhost:5000/")
    login_page = LoginPage(selenium_driver)
    login_page.login("testuser", "testpassword")

    # Step 2: Navigate to the submission history page
    # Assume a known problem id for test user, e.g. 1
    selenium_driver.get("http://localhost:5000/problems/1/solve")
    submission_history_page = SubmissionHistoryPage(selenium_driver)
    submission_history_page.wait_for_table()

    # Step 3: Observe the table of submissions
    rows = submission_history_page.get_table_rows()
    assert len(rows) > 0, "Submission history table should have at least one row"

    # Expected Result: Each submission displays the problem title, status, result, and timestamp
    for row in rows:
        columns = submission_history_page.get_table_columns(row)
        assert len(columns) >= 4, "Each row should have at least 4 columns"
        problem_title = columns[0].text
        status = columns[1].text
        result = columns[2].text
        timestamp = columns[3].text
        assert problem_title, "Problem title should be present"
        assert status, "Status should be present"
        assert result, "Result should be present"
        assert timestamp, "Timestamp should be present"

# --- Playwright Fixtures and Test ---

@pytest.fixture(scope="function")
def playwright_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.mark.tc007
def test_tc007_submission_history_ui_playwright(playwright_browser):
    context = playwright_browser.new_context()
    page = context.new_page()

    # Step 1: Log in as a user
    page.goto("http://localhost:5000/")
    page.wait_for_selector("#login-form")
    page.fill("#login-username", "testuser")
    page.fill("#login-password", "testpassword")
    page.click("#login-form button[type='submit']")

    # Step 2: Navigate to the submission history page
    page.goto("http://localhost:5000/problems/1/solve")
    page.wait_for_selector("#submissionHistory")

    # Step 3: Observe the table of submissions
    rows = page.query_selector_all("#submissionHistory tr")
    assert len(rows) > 0, "Submission history table should have at least one row"

    for row in rows:
        columns = row.query_selector_all("td")
        assert len(columns) >= 4, "Each row should have at least 4 columns"
        problem_title = columns[0].inner_text().strip()
        status = columns[1].inner_text().strip()
        result = columns[2].inner_text().strip()
        timestamp = columns[3].inner_text().strip()
        assert problem_title, "Problem title should be present"
        assert status, "Status should be present"
        assert result, "Result should be present"
        assert timestamp, "Timestamp should be present"

    context.close()