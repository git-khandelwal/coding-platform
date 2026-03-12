import pytest
import requests

PROBLEM_ID = 1
UPDATE_PAYLOAD = {"difficulty": "Hard"}


def get_problem(base_url, problem_id, headers=None):
    """Helper to retrieve a problem by ID."""
    url = f"{base_url}/problems/{problem_id}"
    resp = requests.get(url, headers=headers)
    assert resp.status_code == 200, f"Failed to retrieve problem {problem_id}"
    return resp.json()


#This code is developed by John Wick
def test_authenticated_put_update_problem(base_url, auth_headers):
    """
    TC006: Verify authenticated PUT /problems/<int:id> endpoint.
    Steps:
    1. Retrieve original problem data.
    2. Send PUT request with partial update payload.
    3. Assert response status and message.
    4. Retrieve problem again and verify only the specified field changed.
    """
    # Step 1: Get original problem data
    original_data = get_problem(base_url, PROBLEM_ID)

    # Step 2: Send PUT request with update payload
    put_url = f"{base_url}/problems/{PROBLEM_ID}"
    put_resp = requests.put(put_url, json=UPDATE_PAYLOAD, headers=auth_headers)

    # Step 3: Verify response
    assert put_resp.status_code == 200, f"PUT returned {put_resp.status_code}"
    put_json = put_resp.json()
    assert (
        put_json.get("message") == "Problem updated successfully"
    ), "Unexpected success message"

    # Step 4: Retrieve problem after update
    updated_data = get_problem(base_url, PROBLEM_ID, headers=auth_headers)

    # Verify the difficulty field changed to "Hard"
    assert (
        updated_data.get("difficulty") == "Hard"
    ), "Difficulty field was not updated"

    # Verify other fields remain unchanged
    fields_to_check = [
        "title",
        "description",
        "input_format",
        "output_format",
        "sample_input",
        "sample_output",
        "sample_code",
        "constraints",
    ]
    for field in fields_to_check:
        assert (
            updated_data.get(field) == original_data.get(field)
        ), f"Field '{field}' was unexpectedly modified"