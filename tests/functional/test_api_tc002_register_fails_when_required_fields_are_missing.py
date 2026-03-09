import pytest
import requests
import threading
import time
from werkzeug.serving import make_server

# Import the Flask application instance.
# Adjust the import path if the app is located elsewhere.
from app import app


@pytest.fixture(scope="module")
def flask_server():
    """
    Starts the Flask application in a background thread using Werkzeug's
    development server and yields the base URL for HTTP requests.
    """
    port = 5000
    server = make_server("127.0.0.1", port, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    # Give the server a moment to start.
    time.sleep(0.1)

    yield f"http://127.0.0.1:{port}"

    # Teardown: shut down the server and wait for the thread to finish.
    server.shutdown()
    thread.join()


def test_register_missing_fields(flask_server):
    """
    Test Case TC002: Register fails when required fields are missing.
    """
    base_url = flask_server

    # 1. Send a POST request with only a username.
    response = requests.post(
        f"{base_url}/register",
        json={"username": "testuser"},
    )
    assert response.status_code == 400, "Expected status 400 when password is missing"

    # 2. Send a POST request with only a password.
    response = requests.post(
        f"{base_url}/register",
        json={"password": "secret"},
    )
    assert response.status_code == 400, "Expected status 400 when username is missing"
    assert (
        response.json().get("error") == "Username and password are required"
    ), "Expected error message for missing username and password"

    # 3. Send a POST request with an empty body.
    response = requests.post(
        f"{base_url}/register",
        json={},
    )
    assert response.status_code == 400, "Expected status 400 for empty request body"
    assert (
        response.json().get("error") == "Username and password are required"
    ), "Expected error message for empty request body"