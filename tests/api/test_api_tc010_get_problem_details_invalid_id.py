import pytest
import requests

BASE_URL = "http://localhost:5000"  # Adjust as needed for your environment

@pytest.fixture(scope="module")
def non_existent_problem_id():
    # Assumption: 99999 is a non-existent problem ID in the test environment.
    # If this cannot be guaranteed, this fixture should be updated accordingly.
    return 99999

def test_get_problem_details_invalid_id_returns_404(non_existent_problem_id):
    url = f"{BASE_URL}/problems/{non_existent_problem_id}"
    response = requests.get(url)
    assert response.status_code == 404, f"Expected 404 Not Found, got {response.status_code}"