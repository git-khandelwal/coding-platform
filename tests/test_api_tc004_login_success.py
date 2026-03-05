import json

import pytest
from app import app, db
from app.models import User


@pytest.fixture(scope="module")
def test_client():
    """Create a Flask test client and initialize an in‑memory database."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture(scope="module")
def registered_user(test_client):
    """Register a user that will be used for the login test."""
    user = User(username="testuser")
    user.set_password("testpass")
    db.session.add(user)
    db.session.commit()
    return {"username": "testuser", "password": "testpass"}


def test_login_success(test_client, registered_user):
    """TC004 – Verify that a registered user can log in and receive a JWT token."""
    login_payload = {
        "username": registered_user["username"],
        "password": registered_user["password"],
    }

    response = test_client.post(
        "/login",
        data=json.dumps(login_payload),
        content_type="application/json",
    )

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    data = response.get_json()
    assert data is not None, "Response JSON should not be None"
    assert "access_token" in data, "Response JSON must contain 'access_token'"
    token = data["access_token"]
    assert isinstance(token, str), "access_token should be a string"
    assert token, "access_token should not be empty"