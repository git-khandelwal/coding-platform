import subprocess
import time
import pytest
import requests

# NOTE: The following fixture attempts to start the Flask application for testing.
# The command used to launch the app ("python -m app") is a placeholder and may need
# to be adjusted to match the actual entry point of the application under test.
# If the application cannot be started in this way, this fixture will fail to
# provide a running server, and the test will not execute successfully.
@pytest.fixture(scope="session")
def server():
    """
    Start the Flask application in a subprocess and provide the base URL for tests.
    """
    # Adjust the command below to start your Flask app. For example:
    # process = subprocess.Popen(["flask", "run", "--port", "5000"])
    process = subprocess.Popen(
        ["python", "-m", "app"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Give the server time to start up. In a real-world scenario, you might
    # poll the endpoint until it becomes available instead of using a fixed sleep.
    time.sleep(2)
    base_url = "http://127.0.0.1:5000"
    yield base_url
    # Teardown: terminate the Flask server process
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def test_get_protected_with_empty_token(server):
    """
    TC003: Verify that providing an Authorization header with no token results in an unauthorized error.
    """
    url = f"{server}/protected"
    headers = {"Authorization": "Bearer "}
    response = requests.get(url, headers=headers)

    # Assert that the status code is 401 Unauthorized
    assert response.status_code == 401, f"Expected status 401, got {response.status_code}"

    # Assert that the response body contains an error message indicating missing or invalid token
    try:
        data = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")

    # Common keys for error messages in Flask-JWT-Extended are 'msg' or 'error'
    error_keys = {"msg", "error", "message"}
    assert any(key in data for key in error_keys), (
        f"Response JSON does not contain an expected error key. Received: {data}"
    )
    # Optionally, check that the error message mentions missing or invalid token
    error_message = next((data[key] for key in error_keys if key in data), "")
    assert "token" in error_message.lower() or "missing" in error_message.lower(), (
        f"Error message does not mention missing or invalid token. Received: {error_message}"
    )