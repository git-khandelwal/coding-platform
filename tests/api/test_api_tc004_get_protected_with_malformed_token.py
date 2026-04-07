import os
import time
import threading

import pytest
import requests

# NOTE: The following import assumes that the Flask application instance
# is named `app` and is exposed from the `app` package. Adjust the import
# path if the actual application structure differs.
from app import app  # type: ignore

@pytest.fixture(scope="module")
def flask_server():
    """
    Starts the Flask application in a separate thread using Werkzeug's
    built-in server. The server is started on localhost:5001 and
    shut down after the tests finish.

    This fixture yields the base URL for the running server.
    """
    # Create a WSGI server that can be programmatically shut down
    from werkzeug.serving import make_server

    server = make_server("127.0.0.1", 5001, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    # Give the server a moment to start
    time.sleep(0.5)

    base_url = "http://127.0.0.1:5001"
    yield base_url

    # Teardown: shut down the server
    server.shutdown()
    thread.join()


def test_get_protected_with_malformed_token(flask_server):
    """
    TC004: Verify that an invalid or malformed JWT token results in an
    unauthorized error when accessing the /protected endpoint.
    """
    malformed_token = "this.is.not.a.jwt"
    headers = {"Authorization": f"Bearer {malformed_token}"}

    response = requests.get(f"{flask_server}/protected", headers=headers)

    # Expected: 401 Unauthorized
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    # Expected: JSON body contains an error message indicating invalid token
    try:
        data = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")

    # The error key may vary; common keys are 'msg', 'error', or 'message'
    error_message = (
        data.get("msg") or data.get("error") or data.get("message") or ""
    )
    assert error_message, "Error message not found in response JSON"
    assert (
        "invalid" in error_message.lower()
    ), f"Error message does not indicate invalid token: {error_message}"