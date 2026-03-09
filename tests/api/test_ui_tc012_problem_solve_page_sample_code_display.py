import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Page Object Model for Problem Solve Page ---

class ProblemSolvePage:
    def __init__(self, driver):
        self.driver = driver

    # Assumes code editor is a <textarea id="code-editor"> or similar
    @property
    def code_editor(self):
        return self.driver.find_element(By.ID, "code-editor")

    def get_code_editor_value(self):
        # For <textarea> or <input>
        tag = self.code_editor.tag_name.lower()
        if tag in ["textarea", "input"]:
            return self.code_editor.get_attribute("value")
        # For code editors like Ace/Monaco, adjust as needed
        # Example for Ace: <div class="ace_content">, Monaco: <div class="view-lines">
        try:
            ace = self.driver.find_element(By.CLASS_NAME, "ace_content")
            return ace.text
        except Exception:
            pass
        try:
            monaco = self.driver.find_element(By.CLASS_NAME, "view-lines")
            return monaco.text
        except Exception:
            pass
        # Fallback
        return ""

# --- Fixtures ---

@pytest.fixture(scope="session")
def selenium_driver():
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

@pytest.fixture(scope="session")
def test_user_token():
    # Register and login a user, return JWT token (simulate API call)
    import requests
    import random
    import string
    base_url = "http://localhost:5000"
    username = "tc012user_" + ''.join(random.choices(string.ascii_lowercase, k=6))
    password = "TestPassword123"
    # Register
    requests.post(f"{base_url}/register", json={"username": username, "password": password})
    # Login
    resp = requests.post(f"{base_url}/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    token = resp.json().get("access_token")
    assert token
    return token

@pytest.fixture(scope="session")
def problem_with_sample_code(test_user_token):
    # Create a problem with sample code via API, return problem_id
    import requests
    base_url = "http://localhost:5000"
    headers = {"Authorization": f"Bearer {test_user_token}"}
    payload = {
        "title": "Sample Code Problem TC012",
        "description": "A problem with sample code for TC012.",
        "difficulty": "Easy",
        "input_format": "a=1, b=2",
        "output_format": "3",
        "sample_input": "a=1, b=2",
        "sample_output": "3",
        "sample_code": "def add(a, b):\n    return a + b",
        "constraints": "1 <= a, b <= 100"
    }
    resp = requests.post(f"{base_url}/problems", json=payload, headers=headers)
    assert resp.status_code in (200, 201)
    problem_id = resp.json().get("id")
    assert problem_id
    return problem_id

@pytest.fixture
def authenticated_session(selenium_driver, test_user_token):
    # Set JWT token in localStorage/cookie if required by app
    selenium_driver.get("http://localhost:5000/")
    # Example: set localStorage (adjust as per app's auth mechanism)
    selenium_driver.execute_script(
        "window.localStorage.setItem('access_token', arguments[0]);", test_user_token
    )
    yield

# --- Test Case Implementation ---

def test_tc012_sample_code_displayed_in_editor(
    selenium_driver,
    authenticated_session,
    problem_with_sample_code
):
    """
    TC012: Verify that sample code is displayed if available for the problem.
    Steps:
    1. Navigate to the problem solve page for a problem with sample code.
    2. Observe the code editor area.
    Expected:
    1. Sample code is pre-filled in the code editor.
    """
    base_url = "http://localhost:5000"
    solve_url = f"{base_url}/problems/{problem_with_sample_code}/solve"
    selenium_driver.get(solve_url)

    page = ProblemSolvePage(selenium_driver)

    # Wait for code editor to be present
    try:
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_element_located((By.ID, "code-editor"))
        )
    except Exception as e:
        pytest.fail(f"Code editor not found: {e}")

    # Validate sample code is pre-filled
    sample_code_expected = "def add(a, b):\n    return a + b"
    code_value = page.get_code_editor_value()
    assert sample_code_expected.strip() in code_value.strip(), (
        f"Expected sample code not found in code editor. "
        f"Expected: {sample_code_expected!r}, Found: {code_value!r}"
    )