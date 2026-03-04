import pytest
from app import app as flask_app
from app.models import db, Problem

# NOTE: The following test assumes that the Flask application is configured to use
# SQLAlchemy and that the `Problem` model has the fields used below.  If the
# actual application uses a different database configuration or model
# definitions, the test will need to be adjusted accordingly.

@pytest.fixture(scope="module")
def test_client():
    """
    Create a Flask test client with an in‑memory SQLite database for testing.
    """
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with flask_app.app_context():
        db.create_all()
        client = flask_app.test_client()
        yield client
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_problem(test_client):
    """
    Insert a sample problem into the test database so that the list endpoint
    has at least one entry to display.
    """
    problem = Problem(
        title="Sample Problem",
        description="A simple test problem.",
        difficulty="Easy",
        input_format="",
        output_format="",
        sample_input="",
        sample_output="",
        sample_code="",
        constraints="",
    )
    db.session.add(problem)
    db.session.commit()
    return problem


def test_retrieve_list_of_problems(test_client, sample_problem):
    """
    TC003: Retrieve list of problems (public)
    Verify that a GET request to /problems returns a 200 OK response and that
    the response body contains the titles of all problems.
    """
    response = test_client.get("/problems")
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    # Convert response data to text for easier string matching
    response_text = response.get_data(as_text=True)

    # Check that the sample problem title appears in the rendered HTML
    assert (
        sample_problem.title in response_text
    ), f"Problem title '{sample_problem.title}' not found in response body"

    # Additional generic check: ensure the response contains some HTML tags
    assert "<html" in response_text.lower(), "Response does not contain expected HTML structure"