import pytest
import requests

BASE_URL = "http://localhost:5000"  # Adjust as needed for your environment

@pytest.fixture(scope="module")
def invalid_problem_id():
    # Use a high, likely non-existent ID for negative testing
    return 999999

@pytest.fixture(scope="module")
def problems_details_url(invalid_problem_id):
    return f"{BASE_URL}/problems/{invalid_problem_id}"

def test_get_problem_details_not_found(problems_details_url):
    response = requests.get(problems_details_url)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"