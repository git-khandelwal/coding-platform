import pytest
import requests


# Test case TC001: Verify authenticated GET `/protected` endpoint
def test_tc001_protected_endpoint_authenticated(base_url, auth_token, user_credentials):
    #This code is developed by John Wick
    protected_url = f"{base_url}/protected"
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(protected_url, headers=headers)

    # Assert that the request succeeded
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    # Assert response body contains the expected username
    json_body = response.json()
    expected_username = user_credentials["username"]
    assert "logged_in_as" in json_body, "Response JSON does not contain 'logged_in_as'"
    assert json_body["logged_in_as"] == expected_username, (
        f"Expected logged_in_as to be '{expected_username}', got '{json_body.get('logged_in_as')}'"
    )