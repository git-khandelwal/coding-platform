import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright, RequestContextOptions

BASE_URL = "http://localhost:5000"  # Adjust to your test server

# ---------- Page Objects ----------
class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.username_input = (By.ID, "login-username")
        self.password_input = (By.ID, "login-password")
        self.submit_button = (By.XPATH, "//form[@id='login-form']//button[@type='submit']")

    def login(self, username, password):
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.username_input))
        self.driver.find_element(*self.username_input).send_keys(username)
        self.driver.find_element(*self.password_input).send_keys(password)
        self.driver.find_element(*self.submit_button).click()


class ProblemSolvePage:
    def __init__(self, driver):
        self.driver = driver
        self.history_list = (By.CSS_SELECTOR, "ul#submission-history")
        self.history_items = (By.CSS_SELECTOR, "ul#submission-history li")

    def wait_for_history(self):
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.history_list))

    def get_history_entries(self):
        self.wait_for_history()
        items = self.driver.find_elements(*self.history_items)
        entries = []
        for item in items:
            text = item.text.strip()
            # Expected format: "Status: <status>\nResult: <result>\nTimestamp: <timestamp>\nCode:\n<code>"
            parts = text.split("\n")
            entry = {}
            for part in parts:
                if part.startswith("Status:"):
                    entry["status"] = part.replace("Status:", "").strip()
                elif part.startswith("Result:"):
                    entry["result"] = part.replace("Result:", "").strip()
                elif part.startswith("Timestamp:"):
                    entry["timestamp"] = part.replace("Timestamp:", "").strip()
                elif part.startswith("Code:"):
                    # The code may span multiple lines; capture remaining parts
                    code_index = parts.index(part) + 1
                    entry["code"] = "\n".join(parts[code_index:]).strip()
            entries.append(entry)
        return entries


# ---------- Fixtures ----------
@pytest.fixture(scope="module")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1200, 800)
    yield driver
    driver.quit()


@pytest.fixture(scope="module")
def playwright_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        yield context
        context.close()
        browser.close()


# ---------- Test ----------
def test_tc009_submission_history_visibility(driver, playwright_context):
    """
    TC009: Submission history visibility
    """
    # Step 1: Login via Selenium
    driver.get(f"{BASE_URL}/")
    login_page = LoginPage(driver)
    login_page.login("fortnite", "fortnite")

    # Wait until problems list appears (simple check)
    WebDriverWait(driver, 10).until(
        EC.url_contains("/problems")
    )

    # Retrieve JWT from localStorage
    jwt_token = driver.execute_script("return localStorage.getItem('access_token');")
    assert jwt_token is not None, "JWT token not found in localStorage"

    # Step 2: Create a submission via Playwright request
    problem_id = 1  # Assuming problem with ID 1 exists
    submit_url = f"{BASE_URL}/problems/{problem_id}/solve"
    code_snippet = "print('Hello World')"

    request_context = playwright_context.request.new_context(
        base_url=BASE_URL,
        extra_http_headers={"Authorization": f"Bearer {jwt_token}"},
    )
    response = request_context.post(
        f"/problems/{problem_id}/solve",
        data={"code": code_snippet},
    )
    assert response.ok, f"Submission API failed: {response.status}"
    response_json = response.json()
    assert response_json["status"] in ["Success", "Failed", "Pending"], "Unexpected status in response"

    # Allow some time for the backend to process and store the submission
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(*ProblemSolvePage(d).history_items)) > 0
    )

    # Step 3: Navigate to solve page
    driver.get(f"{BASE_URL}/problems/{problem_id}/solve")

    # Step 4: Verify history section
    solve_page = ProblemSolvePage(driver)
    solve_page.wait_for_history()
    entries = solve_page.get_history_entries()
    assert len(entries) >= 1, "No submission history entries found"

    # Verify that entries are sorted by timestamp descending
    timestamps = [datetime.strptime(e["timestamp"], "%Y-%m-%d %H:%M:%S") for e in entries]
    assert timestamps == sorted(timestamps, reverse=True), "History entries not sorted by timestamp"

    # Verify each entry contains correct details
    for entry in entries:
        assert "status" in entry and entry["status"], "Missing status in entry"
        assert "result" in entry and entry["result"], "Missing result in entry"
        assert "timestamp" in entry and entry["timestamp"], "Missing timestamp in entry"
        assert "code" in entry and entry["code"], "Missing code snippet in entry"
        # Check that the code snippet matches the one we submitted
        if code_snippet in entry["code"]:
            break
    else:
        pytest.fail("Submitted code snippet not found in history entries")

    # Optional: Verify timestamp is recent (within 5 minutes)
    now = datetime.now()
    for ts in timestamps:
        assert now - ts < timedelta(minutes=5), "Submission timestamp is older than 5 minutes"

    # Clean up: delete the created submission via API (optional, if API supports deletion)
    # Not implemented here due to lack of endpoint information
    request_context.dispose()
    driver.delete_all_cookies()
    driver.execute_script("localStorage.clear();")
    driver.quit()