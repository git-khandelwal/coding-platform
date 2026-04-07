# Developed By John Wick
import requests
import pytest

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="session")
def api_base_url():
    return BASE_URL

@pytest.fixture(scope="session")
def http_session():
    session = requests.Session()
    yield session
    session.close()

def test_tc001_retrieve_all_problems(api_base_url, http_session):
    """Test Case TC001: Retrieve all problems (GET)"""
    endpoint = f"{api_base_url}/problems"
    response = http_session.get(endpoint)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    try:
        data = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")
    assert isinstance(data, list), f"Expected response to be a list, got {type(data)}"
    assert len(data) > 0, "Expected non-empty list of problems"
    required_keys = {"id", "title", "difficulty"}
    for idx, problem in enumerate(data):
        assert isinstance(problem, dict), f"Problem at index {idx} is not a dict"
        missing = required_keys - problem.keys()
        assert not missing, f"Problem at index {idx} missing keys: {missing}"
    for problem in data:
        assert isinstance(problem["id"], int), f"id should be int, got {type(problem['id'])}"
        assert isinstance(problem["title"], str), f"title should be str, got {type(problem['title'])}"
        assert isinstance(problem["difficulty"], str), f"difficulty should be str, got {type(problem['difficulty'])}"