import uuid
import json

import pytest
from app import app as flask_app  # Assumes the Flask app is importable from the package `app`


@pytest.fixture
def client():
    """Provide a Flask test client for the application."""
    with flask_app.test_client() as client:
        yield client


def test_duplicate_username_registration(client):
    """
    Test Case TC003: User Registration – Duplicate Username
    """
    # Generate a unique username for the initial registration
    unique_username = f"user_{uuid.uuid4().hex[:8]}"
    password = "TestPass123!"

    # Step 1: Register a user with a unique username
    first_response = client.post(
        "/register",
        data=json.dumps({"username": unique_username, "password": password}),
        content_type="application/json",
    )
    assert first_response.status_code == 201, "Initial registration should succeed with status 201"
    assert (
        first_response.get_json().get("message") == "User registered successfully"
    ), "Initial registration response should contain success message"

    # Step 2: Attempt to register again with the same username
    duplicate_response = client.post(
        "/register",
        data=json.dumps({"username": unique_username, "password": "AnotherPass"}),
        content_type="application/json",
    )
    # Step 3: Verify the response for duplicate registration
    assert duplicate_response.status_code == 400, "Duplicate registration should return 400 Bad Request"
    assert (
        duplicate_response.get_json().get("error") == "Username already exists"
    ), "Duplicate registration response should contain the correct error message"