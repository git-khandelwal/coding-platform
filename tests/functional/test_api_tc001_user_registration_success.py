import uuid
import time
import socket
import threading

import pytest
import requests
from werkzeug.serving import make_server

# Import the Flask application instance
from app import app


@pytest.fixture(scope="module")
def flask_server():
    """
    Starts the Flask application in a background thread and yields the base URL.
    The server is shut down after the tests finish.
    """
    # Find an available port
    sock = socket.socket()
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()

    # Create a WSGI server
    server = make_server("127.0.0.1", port, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    # Give the server a moment to start
    time.sleep(0.1)

    base_url = f"http://127.0.0.1:{port}"
    yield base_url

    # Teardown: shut down the server
    server.shutdown()
    thread.join()


def test_user_registration_success(flask_server):
    """
    TC001: User Registration – Success
    Verifies that a user can be registered with a valid username and password.
    """
    # Generate a unique username to avoid collisions
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "SecurePass123!"

    url = f"{flask_server}/register"
    payload = {"username": username, "password": password}

    response = requests.post(url, json=payload)

    # Assert status code
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"

    # Assert response body
    data = response.json()
    assert data.get("message") == "User registered successfully", (
        f"Unexpected message: {data.get('message')}"
    )
    assert "error" not in data, f"Unexpected error in response: {data.get('error')}"