import os
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """
    Fixture to provide the base URL for the API under test.
    The URL should be set via the BASE_URL environment variable.
    """
    url = os.getenv("BASE_URL")
    if not url:
        pytest.skip("BASE_URL environment variable not set. Skipping TC009.")
    return url.rstrip("/")

def test_tc009_problem_list_retrieval_public(base_url):
    """
    TC009: Problem List Retrieval – Public
    Verify that the /problems endpoint is publicly accessible,
    returns a 200 OK status, and provides either an HTML page
    or a JSON payload listing problems.
    """
    endpoint = f"{base_url}/problems"
    response = requests.get(endpoint, timeout=5)

    # 1. Status 200 OK
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    # 2. Response contains HTML page listing problems (or JSON if API returns)
    content_type = response.headers.get("Content-Type", "")
    assert any(ct in content_type for ct in ("text/html", "application/json")), (
        f"Unexpected Content-Type: {content_type}"
    )

    if "application/json" in content_type:
        # If JSON, ensure it is a list or dict
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Response is not valid JSON")
        assert isinstance(data, (list, dict)), (
            f"Expected JSON list or dict, got {type(data)}"
        )
    else:
        # For HTML, ensure body is not empty and contains <html>
        body = response.text.strip()
        assert body, "Response body is empty"
        assert "<html" in body.lower(), "Response does not contain HTML content"