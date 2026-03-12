import pytest
import requests


def test_tc005_authenticated_get_problems_add(base_url, auth_token):
    #This code is developed by John Wick
    """TC005 – Verify authenticated GET `/problems/add` endpoint."""
    url = f"{base_url}/problems/add"
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(url, headers=headers)

    # Expected Result: 200 OK and HTML form with required fields
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    html = response.text

    required_fields = [
        'name="title"',
        'name="description"',
        'name="difficulty"',
        'name="input_format"',
        'name="output_format"',
        'name="sample_input"',
        'name="sample_output"',
        'name="constraints"',
    ]

    for field in required_fields:
        assert field in html, f"Expected form field {field} not found in response"