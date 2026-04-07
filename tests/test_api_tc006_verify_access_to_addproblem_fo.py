import os
import re

import pytest
import requests


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the API under test."""
    return os.getenv("BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def auth_token(base_url):
    """
    Obtain a valid JWT for an existing test user.
    Adjust the login endpoint and credentials as needed for the target application.
    """
    login_endpoint = f"{base_url}/login"
    credentials = {
        "username": os.getenv("TEST_USERNAME", "testuser"),
        "password": os.getenv("TEST_PASSWORD", "testpass"),
    }
    response = requests.post(login_endpoint, json=credentials)
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    token = data.get("access_token") or data.get("token")
    assert token, "JWT token not found in login response"
    return token


def test_tc006_add_problem_form_authenticated(base_url, auth_token):
    """
    TC006 – Verify access to add‑problem form with authentication.
    """
    url = f"{base_url}/problems/add"
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(url, headers=headers)

    # Assert HTTP 200
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Assert Content-Type is text/html
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type, f"Unexpected Content-Type: {content_type}"

    html = response.text

    # Verify presence of required form fields
    required_fields = [
        r'name=["\']title["\']',
        r'name=["\']description["\']',
        r'name=["\']difficulty["\']',
        r'name=["\']input_format["\']',
        r'name=["\']output_format["\']',
        r'name=["\']sample_input["\']',
        r'name=["\']sample_output["\']',
        r'name=["\']sample_code["\']',
        r'name=["\']constraints["\']',
    ]

    missing = []
    for pattern in required_fields:
        if not re.search(pattern, html, re.IGNORECASE):
            missing.append(pattern)

    assert not missing, f"Missing form fields in HTML: {missing}"