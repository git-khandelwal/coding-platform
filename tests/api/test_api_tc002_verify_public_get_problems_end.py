import pytest


def test_tc002_get_problems_public(base_url, client):
    #This code is developed by John Wick
    """
    TC002: Verify public GET `/problems` endpoint.
    Sends a GET request without authentication and validates the response.
    """
    url = f"{base_url}/problems"
    response = client.get(url)

    # Assert status code is 200 OK
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # Assert the response is HTML
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type.lower(), f"Expected 'text/html' Content-Type, got '{content_type}'"

    # Basic validation that the HTML contains a list of problem titles
    # Look for typical list tags that would hold titles
    html_lower = response.text.lower()
    assert ("<ul" in html_lower and "<li" in html_lower) or ("<ol" in html_lower and "<li" in html_lower), (
        "HTML does not appear to contain a list of problem titles."
    )