import pytest
import requests

# Gaps in context:
# - The base URL of the API is not provided.
# - There is no information on how to create or ensure a problem with a valid ID exists before the test.
# - The structure of the HTML response is not specified.
# - Authentication is not required for this endpoint per code context.

# Please update BASE_URL and provide a valid problem_id for this test to run successfully.

BASE_URL = "http://localhost:5000"  # <-- Update as appropriate for your environment

@pytest.fixture(scope="module")
def valid_problem_id():
    """
    Fixture to provide a valid problem ID.
    This fixture assumes that a problem with ID 1 exists.
    If not, this test will fail.
    """
    # There is no API context for creating a problem without authentication.
    # For now, we use 1 as a placeholder.
    return 1

def test_get_problem_details_returns_html_and_200(valid_problem_id):
    """
    TC009: Verify that problem details can be retrieved for a valid problem ID.
    """
    url = f"{BASE_URL}/problems/{valid_problem_id}"
    response = requests.get(url)

    # Assert status code is 200
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # Assert response contains HTML with problem details
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type or "html" in response.text.lower(), (
        f"Expected HTML content, got Content-Type: {content_type}"
    )

    # Optionally, check for presence of expected HTML elements (if known)
    # For example, if the HTML contains the problem title or description, check for those.
    # Since structure is unknown, we only check for basic HTML tags.
    assert "<html" in response.text.lower(), "Response does not contain HTML content"
    assert "<body" in response.text.lower(), "Response does not contain HTML body"