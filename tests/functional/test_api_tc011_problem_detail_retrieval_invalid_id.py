import pytest
from flask import Flask
from app import app as flask_app  # Adjust import path if necessary

@pytest.fixture(scope="module")
def client():
    """
    Pytest fixture that provides a Flask test client.
    """
    flask_app.testing = True
    with flask_app.test_client() as client:
        yield client

def test_problem_detail_invalid_id(client):
    """
    TC011: Problem Detail Retrieval – Invalid ID
    Attempt to retrieve a problem with a non‑existent ID.
    Expected Result:
        1. Status 404 Not Found
        2. Response contains an error message indicating problem not found.
    Note: The current implementation returns plain text "Problem not found" instead of JSON.
    """
    # Use an ID that is highly unlikely to exist
    nonexistent_id = 999999
    response = client.get(f"/problems/{nonexistent_id}")

    # Assert the status code is 404
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    # Assert the response contains the expected error message
    response_text = response.data.decode("utf-8")
    assert "Problem not found" in response_text, (
        f"Expected error message not found in response: {response_text}"
    )