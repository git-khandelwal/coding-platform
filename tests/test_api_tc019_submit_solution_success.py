import pytest
import requests

# Gaps in context:
# - No base URL is provided for the API.
# - No registration endpoint details or test user credentials are given.
# - No information about a valid problem_id or the structure of a valid code submission.
# - Endpoints for login and their request/response formats are not specified.
# - Cannot assume any default values for user, password, problem, or code.

# Please provide:
# - API base URL
# - Test user credentials (username, password)
# - A valid problem_id for submission
# - A valid code string that will be accepted as "Correct" for the problem
# - Login endpoint and its expected payload/response structure

@pytest.fixture(scope="module")
def api_base_url():
    # GAP: Please provide the API base URL, e.g., "http://localhost:5000"
    return None

@pytest.fixture(scope="module")
def test_user_credentials():
    # GAP: Please provide test user credentials as a dict, e.g., {"username": "testuser", "password": "testpass"}
    return None

@pytest.fixture(scope="module")
def valid_problem_id():
    # GAP: Please provide a valid problem_id as an integer
    return None

@pytest.fixture(scope="module")
def valid_code():
    # GAP: Please provide a valid code string that will be evaluated as "Correct"
    return None

@pytest.fixture(scope="module")
def jwt_token(api_base_url, test_user_credentials):
    # GAP: Please provide the login endpoint and expected payload/response structure
    # Example:
    # login_url = f"{api_base_url}/login"
    # response = requests.post(login_url, json=test_user_credentials)
    # assert response.status_code == 200
    # return response.json()["access_token"]
    return None

def test_submit_solution_success(api_base_url, jwt_token, valid_problem_id, valid_code):
    """
    TC019: Submit Solution Success
    1. Log in to obtain JWT token.
    2. Send POST request to submit solution endpoint with valid code.
    Expected:
    - Response status is 200.
    - Response contains "status": "Success" and "result": "Correct".
    """
    # GAP: Cannot construct endpoint or headers without base URL, token, or problem_id
    assert api_base_url is not None, "API base URL is not provided."
    assert jwt_token is not None, "JWT token is not available. Please provide login endpoint and credentials."
    assert valid_problem_id is not None, "Valid problem_id is not provided."
    assert valid_code is not None, "Valid code for submission is not provided."

    url = f"{api_base_url}/problems/{valid_problem_id}/solve"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "code": valid_code
    }

    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.text}"

    json_resp = response.json()
    assert json_resp.get("status") == "Success", f'Expected status "Success", got {json_resp.get("status")}'
    assert json_resp.get("result") == "Correct", f'Expected result "Correct", got {json_resp.get("result")}'