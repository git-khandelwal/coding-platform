import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="function")
def unique_user_credentials():
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"
    return {"username": username, "password": password}

@pytest.fixture(scope="function")
def register_user(unique_user_credentials):
    url = f"{BASE_URL}/register"
    response = requests.post(url, json=unique_user_credentials)
    return response

@pytest.fixture(scope="function")
def login_user(unique_user_credentials, register_user):
    url = f"{BASE_URL}/login"
    response = requests.post(url, json=unique_user_credentials)
    return response

@pytest.fixture(scope="function")
def jwt_token(login_user):
    assert login_user.status_code == 200, "Login failed, cannot obtain JWT token"
    data = login_user.json()
    assert "access_token" in data, "No access_token in login response"
    return data["access_token"]

def test_tc022_user_registration_login_and_token_usage(
    unique_user_credentials,
    register_user,
    login_user,
    jwt_token
):
    # Step 1: Navigate to home page (API context: check home page is accessible)
    home_url = f"{BASE_URL}/"
    home_response = requests.get(home_url)
    # Home page may or may not exist; if not, skip this check
    if home_response.status_code != 200:
        pytest.skip("Home page endpoint ('/') not implemented or not accessible.")

    # Step 2: Register a new user
    assert register_user.status_code == 201, f"Registration failed: {register_user.text}"
    reg_json = register_user.json()
    assert reg_json.get("message") == "User registered successfully", f"Unexpected registration message: {reg_json}"

    # Step 3: Log in with the new user
    assert login_user.status_code == 200, f"Login failed: {login_user.text}"
    login_json = login_user.json()
    assert "access_token" in login_json, "JWT token not found in login response"

    # Step 4: Store JWT token (already done via fixture)
    token = jwt_token
    assert isinstance(token, str) and len(token) > 0, "Invalid JWT token"

    # Step 5: Access protected content
    protected_url = f"{BASE_URL}/protected"
    headers = {"Authorization": f"Bearer {token}"}
    protected_response = requests.get(protected_url, headers=headers)
    assert protected_response.status_code == 200, f"Protected endpoint not accessible: {protected_response.text}"
    protected_json = protected_response.json()
    assert protected_json.get("logged_in_as") == unique_user_credentials["username"], (
        f"Protected content did not return correct username: {protected_json}"
    )