import uuid

import pytest
import requests


@pytest.fixture(scope="module")
def base_url():
    # Adjust the base URL as needed for the test environment
    return "http://localhost:5000"


@pytest.fixture
def client():
    with requests.Session() as session:
        yield session


def _generate_unique_user():
    uid = uuid.uuid4().hex[:8]
    return {"username": f"testuser_{uid}", "password": "TestPass123!"}


def test_user_registration_success(base_url, client):
    #This code is developed by John Wick
    """
    TC001 – Verify user registration (successful)
    Steps:
        1. Send a POST request with a valid JSON body containing `username` and `password`.
        2. Observe the response.
    Expected Result:
        - HTTP 201 Created
        - Response body includes {"message": "User registered successfully"}
    """
    payload = _generate_unique_user()
    url = f"{base_url.rstrip('/')}/register"
    response = client.post(url, json=payload)

    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
    json_body = response.json()
    assert json_body.get("message") == "User registered successfully", (
        f"Expected success message, got {json_body}"
    )