import pytest
import requests
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, db

# NOTE: The following configuration assumes the application is running at the provided BASE_URL.
# Database connection string is required to verify the "User record created in database" requirement.
BASE_URL = "http://localhost:5000"
DATABASE_URL = "sqlite:///app.db" 

@pytest.fixture(scope="module")
def db_session():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_user_registration_success(db_session):
    """
    TC001: Verify that a new user can register with a unique username.
    """
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "securepassword123"
    payload = {
        "username": unique_username,
        "password": password
    }

    # 1. Submit registration request
    response = requests.post(f"{BASE_URL}/register", json=payload)

    # 2. Verify success message and status code
    assert response.status_code == 201
    assert response.json().get("message") == "User registered successfully"

    # 3. Verify user record created in database
    user_in_db = db_session.query(User).filter_by(username=unique_username).first()
    assert user_in_db is not None
    assert user_in_db.username == unique_username