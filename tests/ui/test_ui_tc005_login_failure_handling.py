import pytest
from playwright.sync_api import sync_playwright, Page, expect

# ----------------------------------------------------------------------
# Page Object Model
# ----------------------------------------------------------------------
class HomePage:
    """Page object for the application's home page."""

    def __init__(self, page: Page):
        self.page = page
        self.url = "/"

    def open(self):
        """Navigate to the home page."""
        self.page.goto(self.url)
        # Wait until the login form is visible
        self.page.wait_for_selector("#login-form", state="visible")

    def login(self, username: str, password: str):
        """Enter credentials and submit the login form."""
        self.page.fill("#login-username", username)
        self.page.fill("#login-password", password)
        # Submit the form by clicking the button
        self.page.click("#login-form button")

    def get_error_message(self) -> str:
        """Retrieve the error message displayed after a failed login."""
        # Wait for the error message to appear
        self.page.wait_for_selector("text=Invalid username or password", timeout=5000)
        # Extract the text content
        return self.page.text_content("text=Invalid username or password")

    def get_local_storage_item(self, key: str) -> str | None:
        """Return the value of a localStorage item, or None if it does not exist."""
        return self.page.evaluate(f"() => localStorage.getItem('{key}')")

# ----------------------------------------------------------------------
# Pytest Fixtures
# ----------------------------------------------------------------------
@pytest.fixture(scope="session")
def playwright_instance():
    """Launch Playwright once per test session."""
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright_instance):
    """Create a browser instance for the test session."""
    browser = playwright_instance.chromium.launch(headless=True)
    yield browser
    browser.close()

@pytest.fixture
def context(browser):
    """Create a new browser context for each test."""
    context = browser.new_context()
    yield context
    context.close()

@pytest.fixture
def page(context):
    """Create a new page for each test."""
    page = context.new_page()
    yield page
    page.close()

@pytest.fixture
def home_page(page) -> HomePage:
    """Instantiate the HomePage object."""
    return HomePage(page)

# ----------------------------------------------------------------------
# Test Case: TC005 - Login failure handling
# ----------------------------------------------------------------------
def test_tc005_login_failure_handling(home_page: HomePage):
    """
    Test that invalid credentials trigger an error message and no token is stored.
    """
    # 1. Open the root URL
    home_page.open()

    # 2. Enter username and incorrect password
    home_page.login(username="fortnite", password="wrongpass")

    # 3. Verify the error message appears
    error_text = home_page.get_error_message()
    assert error_text == "Invalid username or password", (
        f"Expected error message not found. Got: {error_text}"
    )

    # 4. Verify localStorage does not contain an access_token
    token = home_page.get_local_storage_item("access_token")
    assert token is None, f"access_token should not be present, but found: {token}"