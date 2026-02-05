import os
import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def credentials():
    """Credentials for a valid user."""
    return {"username": "testuser", "password": "testpass"}


@pytest.fixture(scope="session")
def auth_token(credentials):
    """Obtain a JWT token via the login endpoint."""
    login_url = f"{BASE_URL}/login"
    response = requests.post(login_url, json=credentials)
    assert response.status_code == 200, f"Login failed with status {response.status_code}"
    data = response.json()
    token = data.get("access_token") or data.get("token")
    assert token, "JWT token not found in login response"
    return token


def test_tc005_authenticated_get_problems_add(auth_token):
    #This code is developed by John Wick
    """TC005 – Verify authenticated GET `/problems/add` endpoint."""
    url = f"{BASE_URL}/problems/add"
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(url, headers=headers)

    # Expected Result: 200 OK and HTML form with required fields
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    html = response.text

    required_fields = [
        'name="title"',
        'name="description"',
        'name="difficulty"',
        'name="input_format"',
        'name="output_format"',
        'name="sample_input"',
        'name="sample_output"',
        'name="constraints"',
    ]

    for field in required_fields:
        assert field in html, f"Expected form field {field} not found in response"