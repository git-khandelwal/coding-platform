import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from playwright.sync_api import sync_playwright

# --- Selenium Page Object Model ---

class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    def login(self, username, password):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login-form"))
        )
        self.driver.find_element(By.ID, "login-username").clear()
        self.driver.find_element(By.ID, "login-username").send_keys(username)
        self.driver.find_element(By.ID, "login-password").clear()
        self.driver.find_element(By.ID, "login-password").send_keys(password)
        self.driver.find_element(By.ID, "login-form").submit()

class NavBar:
    def __init__(self, driver):
        self.driver = driver

    def get_links(self):
        # Wait for navigation bar to be present
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "nav"))
        )
        nav = self.driver.find_element(By.TAG_NAME, "nav")
        links = nav.find_elements(By.TAG_NAME, "a")
        return [link.text.strip() for link in links]

    def has_submissions_link(self):
        links = self.get_links()
        return any("Submissions" in link for link in links)

    def has_add_problem_link(self):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "addProblemLink"))
            )
            return True
        except:
            return False

    def has_logout_link(self):
        links = self.get_links()
        return any("Logout" in link for link in links)

# --- Selenium Fixtures and Test ---

@pytest.fixture(scope="function")
def selenium_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    driver.get("http://localhost:5000")
    yield driver
    driver.quit()

@pytest.mark.tc014
def test_tc014_navbar_links_authenticated_selenium(selenium_driver):
    login_page = LoginPage(selenium_driver)
    nav_bar = NavBar(selenium_driver)

    # Log in as user (assume test user exists)
    login_page.login("testuser", "testpassword")

    # Wait for nav bar to appear after login
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "nav"))
    )

    # Check for Submissions link
    assert nav_bar.has_submissions_link(), "Submissions link not found for authenticated user"

    # Check for Add Problem link (if permitted)
    add_problem_permitted = nav_bar.has_add_problem_link()
    # Add Problem link is optional, so just check presence if permitted

    # Check for Logout link
    assert nav_bar.has_logout_link(), "Logout link not found for authenticated user"

# --- Playwright Fixtures and Test ---

@pytest.fixture(scope="function")
def playwright_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://localhost:5000")
        yield page
        context.close()
        browser.close()

def playwright_login(page, username, password):
    page.wait_for_selector("#login-form")
    page.fill("#login-username", username)
    page.fill("#login-password", password)
    page.click("#login-form button[type='submit']")
    page.wait_for_selector("nav")

def playwright_nav_links(page):
    page.wait_for_selector("nav")
    return [el.inner_text().strip() for el in page.query_selector_all("nav a")]

@pytest.mark.tc014
def test_tc014_navbar_links_authenticated_playwright(playwright_browser):
    page = playwright_browser

    # Log in as user (assume test user exists)
    playwright_login(page, "testuser", "testpassword")

    # Check for Submissions link
    links = playwright_nav_links(page)
    assert any("Submissions" in link for link in links), "Submissions link not found for authenticated user"

    # Check for Add Problem link (if permitted)
    add_problem_link_present = page.query_selector("#addProblemLink") is not None
    # Add Problem link is optional, so just check presence if permitted

    # Check for Logout link
    assert any("Logout" in link for link in links), "Logout link not found for authenticated user"