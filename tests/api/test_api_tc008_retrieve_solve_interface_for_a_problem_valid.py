import os
import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

@pytest.fixture(scope="session")
def auth_token():
    """
    Attempts to obtain a JWT by logging in with credentials supplied via environment variables.
    If the login endpoint or credentials are not available, the test will be skipped.
    """
    login_url = f"{BASE_URL}/login"
    username = os.getenv("TEST_USERNAME")
    password = os.getenv("TEST_PASSWORD")

    if not username or not password:
        pytest.skip("TEST_USERNAME and TEST_PASSWORD environment variables must be set to obtain a JWT.")

    try:
        response = requests.post(login_url, json={"username": username, "password": password})
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Could not reach login endpoint: {e}")

    if response.status_code != 200:
        pytest.skip(f"Login failed with status {response.status_code}: {response.text}")

    data = response.json()
    token = data.get("access_token")
    if not token:
        pytest.skip("Login response did not contain 'access_token'.")

    return token

@pytest.fixture(scope="session")
def problem_id():
    """
    Attempts to retrieve an existing problem ID from the public problems list.
    If the endpoint or data format is not available, the test will be skipped.
    """
    problems_url = f"{BASE_URL}/problems"
    try:
        response = requests.get(problems_url)
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Could not reach problems endpoint: {e}")

    if response.status_code != 200:
        pytest.skip(f"Problems endpoint returned status {response.status_code}: {response.text}")

    # The application renders an HTML page; we attempt to extract the first problem ID
    # from a data attribute or link. If parsing fails, skip the test.
    # This is a best‑effort approach; adjust the parsing logic as needed.
    text = response.text
    # Look for a pattern like /problems/<id> in the HTML
    import re
    match = re.search(r'/problems/(\d+)', text)
    if not match:
        pytest.skip("Could not find a problem ID in the problems page.")
    return int(match.group(1))

def test_retrieve_solve_interface_valid(auth_token, problem_id):
    """
    TC008: Retrieve solve interface for a problem (valid)
    """
    url = f"{BASE_URL}/problems/{problem_id}/solve"
    headers = {"Authorization": f"Bearer {auth_token}"}

    response = requests.get(url, headers=headers)

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    # Check that the response contains HTML with a code editor.
    # The exact marker may vary; here we look for a common phrase.
    assert "code editor" in response.text.lower(), "Response does not contain a code editor."
    assert "<html" in response.text.lower(), "Response does not appear to be an HTML page."
    assert "<body" in response.text.lower(), "Response does not contain a body tag."
    assert "<div" in response.text.lower(), "Response does not contain any div elements."