import os
import pytest
import requests

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------
@pytest.fixture(scope="session")
def base_url():
    """
    Base URL of the API under test.

    The actual URL is not provided in the test case description.
    It can be supplied via the `API_BASE_URL` environment variable.
    If not set, it defaults to ``http://localhost:5000``.
    """
    return os.getenv("API_BASE_URL", "http://localhost:5000")


@pytest.fixture
def nonexistent_problem_id():
    """
    Problem ID that is expected not to exist.
    The test case suggests using ``9999``.
    """
    return 9999


# ----------------------------------------------------------------------
# Test case: TC005 – Retrieve non‑existent problem details
# ----------------------------------------------------------------------
def test_tc005_retrieve_nonexistent_problem_details(base_url, nonexistent_problem_id):
    """
    Verify that requesting an invalid problem ID returns a 404 Not Found
    error and an appropriate error message.

    Steps:
    1. Send a GET request to ``/problems/<id>`` with a non‑existent ID.
    2. Assert that the response status code is 404.
    3. Assert that the response body contains an error message indicating
       the problem does not exist.

    Note:
    The exact format of the error message is not defined in the provided
    documentation. The assertion checks for a generic substring that is
    commonly used in the application (``Problem not found``). Adjust the
    assertion as needed to match the actual implementation.
    """
    url = f"{base_url}/problems/{nonexistent_problem_id}"
    response = requests.get(url)

    # Assert HTTP status code
    assert response.status_code == 404, f"Expected 404 Not Found, got {response.status_code}"

    # Assert error message in response body
    # The response may be plain text, JSON, or HTML. We perform a flexible check.
    content = response.text
    expected_substring = "Problem not found"
    assert expected_substring in content, (
        f"Expected error message containing '{expected_substring}' in response body, "
        f"but got: {content!r}"
    )