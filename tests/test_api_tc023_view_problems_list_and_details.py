import pytest
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def problems_list_response():
    """
    Fixture to get the problems list page as an unauthenticated user.
    """
    url = f"{BASE_URL}/problems"
    response = requests.get(url)
    return response

@pytest.fixture(scope="module")
def first_problem_id(problems_list_response):
    """
    Fixture to extract the first problem's ID from the problems list HTML.
    Returns None if no problem is found.
    """
    soup = BeautifulSoup(problems_list_response.text, "html.parser")
    # Try to find a link to a problem details page: <a href="/problems/<id>">
    link = soup.find("a", href=lambda x: x and x.startswith("/problems/") and x[10:].isdigit())
    if link:
        # Extract the problem ID from the href
        try:
            problem_id = int(link['href'].split("/problems/")[1].split("/")[0])
            return problem_id
        except Exception:
            return None
    return None

def test_tc023_view_problems_list_and_details(problems_list_response, first_problem_id):
    """
    TC023: Test viewing the problems list and accessing problem details as an unauthenticated user.
    Steps:
    1. Navigate to problems list page.
    2. View list of problems.
    3. Click on a problem to view details.
    Expected:
    1. Problems list is displayed.
    2. Problem details are shown.
    """
    # Step 1 & 2: Problems list is displayed
    response = problems_list_response
    assert response.status_code == 200, "Problems list page should return 200 OK"
    assert "html" in response.headers.get("Content-Type", ""), "Problems list response should be HTML"
    soup = BeautifulSoup(response.text, "html.parser")
    # Check that at least one problem is listed (assume at least one <a href="/problems/<id>">)
    problem_links = soup.find_all("a", href=lambda x: x and x.startswith("/problems/") and x[10:].isdigit())
    assert problem_links, "Problems list should contain at least one problem link"

    # Step 3: Click on a problem to view details
    assert first_problem_id is not None, "Could not extract a problem ID from the problems list"
    details_url = f"{BASE_URL}/problems/{first_problem_id}"
    details_response = requests.get(details_url)
    assert details_response.status_code == 200, f"Problem details page for problem {first_problem_id} should return 200 OK"
    assert "html" in details_response.headers.get("Content-Type", ""), "Problem details response should be HTML"
    details_soup = BeautifulSoup(details_response.text, "html.parser")
    # Check that some expected problem detail fields are present in the HTML
    # (e.g., title, description, etc. - we look for generic presence of text)
    assert details_soup.text.strip(), "Problem details page should not be empty"
    # Optionally, check that the problem title appears somewhere (if available)
    # title = details_soup.find("h1") or details_soup.find("h2")
    # assert title and title.text.strip(), "Problem details page should display a title"