import os
import socket
import threading
import time

import pytest
import requests

# The following imports assume that the Flask application, database, and User model
# are exposed from the package `app`. Adjust the import paths if your project
# structure differs.
try:
    from app import app as flask_app, db, User
except Exception as e:
    raise ImportError(
        "Could not import the Flask app, db, or User model. "
        "Ensure that the application package is importable and contains "
        "the expected objects."
    ) from e


@pytest.fixture(scope="session")
def flask_app_server():
    """
    Starts the Flask application in a background thread and yields the base URL.
    The database is configured to use an in-memory SQLite instance for isolation.
    """
    # Configure the app for testing
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    flask_app.config["JWT_SECRET_KEY"] = "test-secret-key"
    flask_app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour

    # Create database tables
    with flask_app.app_context():
        db.create_all()

        # Create a test user
        test_user = User(username="testuser")
        test_user.set_password("testpass")
        db.session.add(test_user)
        db.session.commit()

    # Find an available port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        port = s.getsockname()[1]

    # Start the Flask app in a separate thread
    def run_app():
        flask_app.run(port=port, use_reloader=False, debug=False)

    server_thread = threading.Thread(target=run_app, daemon=True)
    server_thread.start()

    # Wait briefly for the server to start
    time.sleep(1)

    base_url = f"http://127.0.0.1:{port}"
    yield base_url

    # Teardown: the daemon thread will exit when the main process exits


def test_user_login_success(flask_app_server):
    """
    Test Case TC004: User Login – Success
    Sends a POST request to /login with valid credentials and verifies that
    the response status is 200 and contains an access_token in the JSON body.
    """
    login_url = f"{flask_app_server}/login"
    payload = {"username": "testuser", "password": "testpass"}

    response = requests.post(login_url, json=payload)

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    json_data = response.json()
    assert "access_token" in json_data, "Response JSON does not contain 'access_token'"
    assert isinstance(json_data["access_token"], str) and json_data["access_token"], (
        "access_token should be a non-empty string"
    )