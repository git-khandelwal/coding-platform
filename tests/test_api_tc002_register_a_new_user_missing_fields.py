import pytest
from flask import Flask

# Import the Flask application and database objects
# Adjust the import path according to your project structure
# For example, if your app package is named `app`, use:
#   from app import app as flask_app, db
#   from app.models import User
# Replace the following imports with the correct ones for your project.

from app import app as flask_app
from app import db
from app.models import User


@pytest.fixture(scope="module")
def app() -> Flask:
    """Configure the Flask application for testing."""
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    return flask_app


@pytest.fixture(scope="module")
def client(app: Flask):
    """Provide a test client for the Flask application."""
    return app.test_client()


@pytest.fixture(scope="module", autouse=True)
def setup_database(app: Flask):
    """Create database tables before tests and drop them after."""
    with app.app_context():
        db.create_all()
    yield
    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_register_missing_fields(client):
    """
    Verify that registration fails when required fields are omitted.
    """
    # Test case: missing username
    response = client.post(
        "/register",
        json={"password": "StrongPassword123"},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400, "Expected status 400 for missing username"
    data = response.get_json()
    assert data is not None, "Response should contain JSON"
    assert (
        data.get("error") == "Username and password are required"
    ), "Error message mismatch for missing username"

    # Test case: missing password
    response = client.post(
        "/register",
        json={"username": "testuser"},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400, "Expected status 400 for missing password"
    data = response.get_json()
    assert data is not None, "Response should contain JSON"
    assert (
        data.get("error") == "Username and password are required"
    ), "Error message mismatch for missing password"