import pytest
from app import app


@pytest.fixture
def client():
    """
    Provides a Flask test client for making HTTP requests to the application.
    """
    with app.test_client() as client:
        yield client


def _obtain_valid_jwt(client):
    """
    Placeholder for obtaining a valid JWT.

    The actual implementation depends on the authentication endpoint
    (e.g., POST /login with username/password). Since the login
    endpoint and credentials are not provided in the available context,
    this function raises NotImplementedError.

    Replace this function with real logic once the authentication
    mechanism is known.
    """
    raise NotImplementedError(
        "JWT acquisition logic is not implemented. "
        "Provide a login endpoint and valid credentials."
    )


@pytest.mark.skip(reason="JWT acquisition not implemented; cannot perform authenticated request.")
def test_tc006_access_add_problem_form_with_valid_jwt(client):
    """
    TC006: Access add‑problem form with valid JWT

    Steps:
    1. Obtain a valid JWT.
    2. Send a GET request to the add‑problem form endpoint with the token.

    Expected Result:
    1. Response status 200 OK.
    2. Response body contains HTML form for adding a problem.
    """
    token = _obtain_valid_jwt(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/problems/add", headers=headers)

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert b"<form" in response.data, "Response does not contain an HTML form"
    assert b"add_problem.html" in response.data or b"add_problem" in response.data, \
        "Response does not appear to be the add problem form page"