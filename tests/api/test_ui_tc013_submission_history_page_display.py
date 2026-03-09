import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

# --- Page Objects ---

class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    def login(self, username, password):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login-form"))
        )
        self.driver.find_element(By.ID, "login-username").clear()
        self.driver.find_element(By.ID, "login-username").send_keys(username)
        self.driver.find_element(By.ID, "login-password").clear()
        self.driver.find_element(By.ID, "login-password").send_keys(password)
        self.driver.find_element(By.XPATH, "//form[@id='login-form']//button[@type='submit']").click()

class SubmissionHistoryPage:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_page(self):
        # Wait for the submissions list/table to appear
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".submission-list, .submission-history, ul, table"))
        )

    def get_submissions(self):
        # Try to find submissions in a table or list
        submissions = []
        try:
            # Table format
            table = self.driver.find_element(By.TAG_NAME, "table")
            rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # skip header
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 3:
                    submissions.append({
                        "status": cells[1].text,
                        "result": cells[2].text,
                        "timestamp": cells[3].text if len(cells) > 3 else "",
                    })
        except:
            # List format (ul > li)
            try:
                lis = self.driver.find_elements(By.CSS_SELECTOR, "ul li")
                for li in lis:
                    text = li.text
                    # Try to parse status, result, timestamp from text
                    # e.g. "Status: Accepted | Result: OK | Timestamp: 2024-06-01 15:00:00"
                    parts = [p.strip() for p in text.split('|')]
                    data = {}
                    for part in parts:
                        if ':' in part:
                            k, v = part.split(':', 1)
                            data[k.strip().lower()] = v.strip()
                    if "status" in data and "result" in data and "timestamp" in data:
                        submissions.append({
                            "status": data["status"],
                            "result": data["result"],
                            "timestamp": data["timestamp"],
                        })
            except:
                pass
        return submissions

# --- Fixtures ---

@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1400,900")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)
    yield driver
    driver.quit()

@pytest.fixture(scope="module")
def base_url():
    # Adjust this to your application's base URL
    return "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user():
    # Static test user; ensure this user exists and has submissions
    return {"username": "testuser", "password": "testpass"}

# --- Test Case TC013 ---

def test_tc013_submission_history_page_display(driver, base_url, test_user):
    # Step 1: Login
    driver.get(base_url)
    login_page = LoginPage(driver)
    login_page.login(test_user["username"], test_user["password"])

    # Wait for login to complete (e.g., look for a protected element or redirect)
    # Here we wait for a known element or just sleep briefly if no redirect
    time.sleep(1)

    # Step 2: Navigate to the submission history page
    # Adjust the URL if your app uses a different path
    driver.get(f"{base_url}/submissions")

    submission_page = SubmissionHistoryPage(driver)
    submission_page.wait_for_page()

    # Step 3: Observe the list of submissions
    submissions = submission_page.get_submissions()

    # There should be at least one submission for this test to be valid
    assert submissions, "No submissions found for the user."

    # Step 4: Each submission shows status, result, and timestamp
    for submission in submissions:
        assert submission["status"], "Submission status is missing."
        assert submission["result"], "Submission result is missing."
        assert submission["timestamp"], "Submission timestamp is missing."
        # Optionally, check timestamp format
        assert len(submission["timestamp"]) >= 10, "Timestamp format seems invalid."