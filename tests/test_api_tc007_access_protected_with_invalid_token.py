import pytest
import requests

# Gaps in context:
# - The base URL of the API is not provided.
# - The exact path of the protected endpoint is assumed from code context to be '/protected'.
# - No authentication or user setup is needed for this negative test.

@pytest.fixture(scope="module")
def api_base_url():
    # GAP: Please provide the correct base URL for the API under test.
    return "http://localhost:5000"

@pytest.mark.parametrize("headers", [
    {},  # No Authorization header
    {"Authorization": "Bearer invalidtoken123"},  # Invalid token
])
def test_access_protected_with_invalid_or_missing_token(api_base_url, headers):
    """
    TC007: Access Protected with Invalid Token
    Verify access to protected endpoint with an invalid or missing token is denied.
    """
    url = f"{api_base_url}/protected"
    response = requests.get(url, headers=headers)
    assert response.status_code == 401, (
        f"Expected status code 401, got {response.status_code}. "
        f"Response body: {response.text}"
    )