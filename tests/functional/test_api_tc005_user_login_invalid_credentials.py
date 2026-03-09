import pytest
from app import app, db

@pytest.fixture(scope='module')
def test_app():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def client(test_app):
    return test_app.test_client()

@pytest.fixture(scope='module')
def registered_user(client):
    payload = {'username': 'testuser', 'password': 'correctpassword'}
    response = client.post('/register', json=payload)
    assert response.status_code == 201, f"Registration failed: {response.get_data(as_text=True)}"
    return payload['username']

def test_tc005_user_login_invalid_credentials(client, registered_user):
    """
    TC005: User Login – Invalid Credentials
    Attempt login with incorrect password.
    """
    payload = {'username': registered_user, 'password': 'wrongpassword'}
    response = client.post('/login', json=payload)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    assert response.is_json, "Response is not JSON"
    data = response.get_json()
    assert 'error' in data, "Response JSON does not contain 'error' key"
    assert data['error'] == 'Invalid username or password', f"Unexpected error message: {data['error']}"