import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LOGIN_URL = "http://localhost:5000/"
SUBMISSION_HISTORY_URL = "http://localhost:5000/submissions"

USERNAME = "test"
PASSWORD = "1234"

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

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

class SubmissionHistoryPage:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_page(self):
        # Wait for either the empty message or a submission entry
        WebDriverWait(self.driver, 10).until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'no submissions') or contains(text(), 'No submissions')]")),
                EC.presence_of_element_located((By.ID, "submissionHistory"))
            )
        )

    def get_empty_message(self):
        # Try to find a message indicating no submissions
        possible_selectors = [
            (By.XPATH, "//*[contains(text(), 'no submissions') or contains(text(), 'No submissions')]"),
            (By.XPATH, "//*[contains(text(), 'No submission') or contains(text(), 'no submission')]"),
        ]
        for by, value in possible_selectors:
            elements = self.driver.find_elements(by, value)
            if elements:
                return elements[0].text
        return None

    def has_submission_entries(self):
        # Look for a submission history table/list
        entries = self.driver.find_elements(By.CSS_SELECTOR, "#submissionHistory tr, #submissionHistory .submission-entry")
        return len(entries) > 0

@pytest.mark.usefixtures("driver")
def test_TC011_submission_history_no_submissions(driver):
    # Step 1: Login as test user
    driver.get(LOGIN_URL)
    login_page = LoginPage(driver)
    login_page.login(USERNAME, PASSWORD)

    # Step 2: Navigate to submission history page
    driver.get(SUBMISSION_HISTORY_URL)
    submission_history_page = SubmissionHistoryPage(driver)
    submission_history_page.wait_for_page()

    # Step 3: Assert the empty message is shown and no submission entries are present
    empty_message = submission_history_page.get_empty_message()
    assert empty_message is not None, "Expected a message indicating no submissions are available."
    assert "no submissions" in empty_message.lower() or "no submission" in empty_message.lower(), \
        f"Expected empty submission message, got: {empty_message}"

    assert not submission_history_page.has_submission_entries(), \
        "Expected no submission entries to be displayed for a user with no submissions."