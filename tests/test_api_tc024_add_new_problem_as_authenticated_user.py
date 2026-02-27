import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user_credentials():
    # These credentials should exist in the test DB, or registration logic should be added
    return {
        "username": "testuser_tc024",
        "password": "TestPass123!"
    }

@pytest.fixture(scope="module")
def auth_token(test_user_credentials):
    # Register user (ignore if already exists)
    reg_resp = requests.post(
        f"{BASE_URL}/register",
        json={
            "username": test_user_credentials["username"],
            "password": test_user_credentials["password"]
        }
    )
    # Login user
    login_resp = requests.post(
        f"{BASE_URL}/login",
        json={
            "username": test_user_credentials["username"],
            "password": test_user_credentials["password"]
        }
    )
    assert login_resp.status_code == 200
    token = login_resp.json().get("access_token")
    assert token is not None
    return token

@pytest.fixture
def problem_data():
    return {
        "title": "TC024 Sample Problem",
        "description": "Sample description for TC024.",
        "difficulty": "Easy",
        "input_format": "Input format details.",
        "output_format": "Output format details.",
        "sample_input": "1 2",
        "sample_output": "3",
        "sample_code": "print(sum(map(int, input().split())))",
        "constraints": "1 <= n <= 1000"
    }

def test_add_new_problem_as_authenticated_user(auth_token, problem_data):
    # Step 1: Access add problem form (GET /problems/add)
    headers = {"Authorization": f"Bearer {auth_token}"}
    get_form_resp = requests.get(f"{BASE_URL}/problems/add", headers=headers)
    assert get_form_resp.status_code == 200
    assert "Add Problem" in get_form_resp.text or "form" in get_form_resp.text.lower()

    # Step 2: Submit new problem (POST /problems/add)
    post_resp = requests.post(
        f"{BASE_URL}/problems/add",
        json=problem_data,
        headers=headers
    )
    assert post_resp.status_code == 201
    resp_json = post_resp.json()
    assert resp_json.get("message") == "Problem added successfully"
    assert resp_json.get("problem") is not None
    assert resp_json["problem"]["title"] == problem_data["title"]

    # Step 3: Verify problem appears in list (GET /problems)
    list_resp = requests.get(f"{BASE_URL}/problems")
    assert list_resp.status_code == 200
    # Since /problems returns HTML, check if problem title is present in the response
    assert problem_data["title"] in list_resp.text

    # Cleanup: Optionally, delete the created problem (if API supports it)
    # Not implemented here due to lack of API details for problem lookup and deletion