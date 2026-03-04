import threading
import time

import pytest
import requests
from werkzeug.serving import make_server

# Import the Flask application instance.
# Adjust the import path if the app instance is located elsewhere.
from app import app as flask_app


@pytest.fixture(scope="module")
def server():
    """
    Starts the Flask application in a separate thread using Werkzeug's
    built-in server. Yields the base URL for the test client to use.
    """
    # Create a WSGI server bound to localhost on an arbitrary port.
    http_server = make_server("127.0.0.1", 5000, flask_app)
    thread = threading.Thread(target=http_server.serve_forever)
    thread.daemon = True
    thread.start()

    # Give the server a moment to start.
    time.sleep(0.5)

    base_url = "http://127.0.0.1:5000"
    yield base_url

    # Teardown: shut down the server and wait for the thread to finish.
    http_server.shutdown()
    thread.join()


def test_access_add_problem_form_without_jwt(server):
    """
    TC007: Access add‑problem form without JWT
    Verify that a GET request to /problems/add without an Authorization header
    returns a 401 Unauthorized response and contains an error message in JSON.
    """
    url = f"{server}/problems/add"
    response = requests.get(url)

    # Assert the HTTP status code is 401 Unauthorized.
    assert response.status_code == 401, (
        f"Expected status 401, got {response.status_code}. "
        f"Response body: {response.text}"
    )

    # Assert the response body is JSON and contains an error message.
    try:
        json_body = response.json()
    except ValueError:
        pytest.fail(f"Response is not valid JSON: {response.text}")

    # Flask-JWT-Extended typically returns a 'msg' key for error messages.
    assert "msg" in json_body, (
        f"Expected 'msg' key in JSON response, got: {json_body}"
    )
    assert isinstance(json_body["msg"], str) and json_body["msg"], (
        f"Error message should be a non-empty string, got: {json_body['msg']}"
    )