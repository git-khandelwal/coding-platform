import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:5000"

TEST_USER = {
    "username": "testuser_tc027",
    "password": "TestPass123!"
}

TEST_PROBLEM = {
    "title": "TC027 Problem",
    "description": "Original description",
    "difficulty": "Easy",
    "input_format": "int n",
    "output_format": "int result",
    "sample_input": "1",
    "sample_output": "2",
    "sample_code": "def solve(n):\n    return n+1",
    "constraints": "1 <= n <= 100"
}

EDITED_PROBLEM = {
    "title": "TC027 Problem Edited",
    "description": "Edited description"
}

@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)
    yield driver
    driver.quit()

def register_user(driver):
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "register-form")))
    driver.find_element(By.ID, "register-username").clear()
    driver.find_element(By.ID, "register-username").send_keys(TEST_USER["username"])
    driver.find_element(By.ID, "register-password").clear()
    driver.find_element(By.ID, "register-password").send_keys(TEST_USER["password"])
    driver.find_element(By.CSS_SELECTOR, "#register-form button[type='submit']").click()
    # Registration may show an alert or message, ignore if already registered

def login_user(driver):
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-form")))
    driver.find_element(By.ID, "login-username").clear()
    driver.find_element(By.ID, "login-username").send_keys(TEST_USER["username"])
    driver.find_element(By.ID, "login-password").clear()
    driver.find_element(By.ID, "login-password").send_keys(TEST_USER["password"])
    driver.find_element(By.CSS_SELECTOR, "#login-form button[type='submit']").click()
    # Wait for login to complete (could check for protected content or redirect)
    time.sleep(1)

def add_problem_via_api():
    import requests
    # Login to get JWT token
    login_resp = requests.post(f"{BASE_URL}/login", json={
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    })
    assert login_resp.status_code == 200
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    # Add problem
    resp = requests.post(f"{BASE_URL}/problems/add", json=TEST_PROBLEM, headers=headers)
    assert resp.status_code in (200, 201)
    # Get problem id from list
    list_resp = requests.get(f"{BASE_URL}/problems")
    assert list_resp.status_code == 200
    problems = list_resp.json() if list_resp.headers.get("Content-Type", "").startswith("application/json") else []
    for p in problems:
        if p.get("title") == TEST_PROBLEM["title"]:
            return p["id"]
    # If not found, fallback to scraping
    return None

def get_problem_id_by_title(driver, title):
    driver.get(f"{BASE_URL}/problems")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    links = driver.find_elements(By.LINK_TEXT, title)
    if links:
        href = links[0].get_attribute("href")
        # Assume /problems/<id>
        try:
            return int(href.rstrip("/").split("/")[-1])
        except Exception:
            return None
    return None

class ProblemsListPage:
    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(f"{BASE_URL}/problems")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    def open_problem_by_title(self, title):
        link = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, title))
        )
        link.click()

    def is_problem_present(self, title):
        self.open()
        links = self.driver.find_elements(By.LINK_TEXT, title)
        return bool(links)

class ProblemDetailsPage:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_loaded(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

    def click_edit(self):
        edit_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Edit"))
        )
        edit_btn.click()

    def click_delete(self):
        delete_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Delete"))
        )
        delete_btn.click()
        # Confirm dialog if present
        try:
            alert = WebDriverWait(self.driver, 2).until(EC.alert_is_present())
            alert.accept()
        except Exception:
            pass

    def get_title(self):
        return self.driver.find_element(By.TAG_NAME, "h2").text

    def has_edit_and_delete(self):
        edit = self.driver.find_elements(By.LINK_TEXT, "Edit")
        delete = self.driver.find_elements(By.LINK_TEXT, "Delete")
        return bool(edit) and bool(delete)

class ProblemEditPage:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_loaded(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )

    def edit_title_and_description(self, title, description):
        title_input = self.driver.find_element(By.NAME, "title")
        desc_input = self.driver.find_element(By.NAME, "description")
        title_input.clear()
        title_input.send_keys(title)
        desc_input.clear()
        desc_input.send_keys(description)

    def save(self):
        btn = self.driver.find_element(By.CSS_SELECTOR, "form button[type='submit']")
        btn.click()

@pytest.fixture(scope="module")
def ensure_test_user_and_problem(driver):
    register_user(driver)
    login_user(driver)
    # Add problem via API for reliability
    problem_id = add_problem_via_api()
    yield problem_id
    # Teardown: try to delete the problem if it still exists
    import requests
    login_resp = requests.post(f"{BASE_URL}/login", json={
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    })
    if login_resp.status_code == 200:
        token = login_resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        if problem_id:
            requests.delete(f"{BASE_URL}/problems/{problem_id}", headers=headers)

def test_tc027_edit_and_delete_problem_authenticated_user(driver, ensure_test_user_and_problem):
    problem_id = ensure_test_user_and_problem
    login_user(driver)
    problems_list = ProblemsListPage(driver)
    problems_list.open()
    assert problems_list.is_problem_present(TEST_PROBLEM["title"]), "Problem not found in list after creation"

    # Step 2: Navigate to problem details page
    problems_list.open_problem_by_title(TEST_PROBLEM["title"])
    details = ProblemDetailsPage(driver)
    details.wait_for_loaded()

    # Step 1/Expected: Edit and delete options are available
    assert details.has_edit_and_delete(), "Edit and Delete options not available"

    # Step 3: Edit problem details and save
    details.click_edit()
    edit_page = ProblemEditPage(driver)
    edit_page.wait_for_loaded()
    edit_page.edit_title_and_description(EDITED_PROBLEM["title"], EDITED_PROBLEM["description"])
    edit_page.save()

    # After save, should be redirected to details page
    details = ProblemDetailsPage(driver)
    details.wait_for_loaded()
    assert details.get_title() == EDITED_PROBLEM["title"], "Problem title not updated after edit"

    # Step 4: Delete problem
    details.click_delete()
    # Wait for redirect to problems list
    problems_list.open()
    time.sleep(1)  # Wait for deletion to propagate

    # Step 5: Verify problem is removed from list
    assert not problems_list.is_problem_present(EDITED_PROBLEM["title"]), "Problem still present in list after deletion"