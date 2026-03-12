import pytest
import requests


def test_get_problem_submissions(base_url, auth_token):
    #This code is developed by John Wick
    """
    TC008: Verify authenticated GET `/problems/<int:problem_id>/submissions` endpoint.
    """
    problem_id = 1
    url = f"{base_url}/problems/{problem_id}/submissions"
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(url, headers=headers)

    # Expected Result: 200 OK and JSON array of submission objects
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    submissions = response.json()
    assert isinstance(submissions, list), "Response body should be a JSON array"

    # Validate structure of each submission object if any are returned
    required_keys = {"problem_title", "status", "result", "timestamp", "code"}
    for submission in submissions:
        assert isinstance(submission, dict), "Each submission entry should be a JSON object"
        missing = required_keys - submission.keys()
        assert not missing, f"Submission object missing keys: {missing}"