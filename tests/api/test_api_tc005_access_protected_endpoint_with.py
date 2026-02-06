# Developed By John Wick
import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="session")
def session():
    """Provide a requests session for the test."""
    with requests.Session() as s:
        yield s

def test_access_protected_endpoint_without_token(session):
    """
    TC005: Access protected endpoint without token (GET)
    Verify that a GET request to the protected endpoint without a JWT returns a 401 error.
    """
    url = f"{BASE_URL}/protected"
    response = session.get(url)

    # Assert status code is 401 Unauthorized
    assert response.status_code == 401, f"Expected status 401, got {response.status_code}"

    # Assert response body contains error message indicating missing or invalid token
    try:
        data = response.json()
    except ValueError:
        pytest.fail("Response is not JSON")

    # Flask-JWT-Extended default message for missing token
    assert "msg" in data, "Response JSON does not contain 'msg' key"
    assert data["msg"] in ("Missing Authorization Header", "Missing Token", "Missing JWT"), \
        f"Unexpected error message: {data['msg']}"