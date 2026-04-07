import pytest
import requests

@pytest.fixture(scope="module")
def api_base_url():
    # GAP: The base URL of the API is not specified in the provided context.
    # Please provide the API base URL (e.g., http://localhost:5000 or similar).
    raise NotImplementedError("API base URL is not specified. Please provide the base URL for the API.")

@pytest.fixture
def protected_route():
    # GAP: The exact protected route path is not specified.
    # From code context, '/protected' is a protected route.
    return "/protected"

def test_access_protected_route_without_token(api_base_url, protected_route):
    url = api_base_url + protected_route
    response = requests.get(url)
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"