import pytest
from app import app as flask_app, db, Problem  # Adjust import path if necessary

@pytest.fixture(scope="module")
def test_client():
    """
    Set up a Flask test client with an in‑memory SQLite database.
    A single problem is created for the test case.
    """
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with flask_app.app_context():
        db.create_all()

        # Create a problem instance
        problem = Problem(
            title="Sample Problem",
            description="This is a sample problem.",
            difficulty="Easy",
            input_format="Input format",
            output_format="Output format",
            sample_input="Sample input",
            sample_output="Sample output",
            sample_code='print("Hello")',
            constraints="None",
        )
        db.session.add(problem)
        db.session.commit()
        problem_id = problem.id

        yield flask_app.test_client(), problem_id

        # Teardown: drop all tables
        db.session.remove()
        db.drop_all()


def test_problem_detail_valid_id(test_client):
    """
    TC010 – Problem Detail Retrieval – Valid ID
    """
    client, problem_id = test_client
    response = client.get(f"/problems/{problem_id}")

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    content = response.get_data(as_text=True)

    # Verify that the response contains the problem details
    assert "Sample Problem" in content, "Problem title not found in response"
    assert "This is a sample problem." in content, "Problem description not found in response"
    # Additional checks can be added if the HTML structure is known