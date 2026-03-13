import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Page Object for Navigation Bar (assumes nav links are <a> elements)
class NavigationBar:
    def __init__(self, driver):
        self.driver = driver

    def get_nav_links(self):
        # Only select visible <a> elements (robust selector: visible text)
        links = self.driver.find_elements(By.TAG_NAME, "a")
        visible_links = [link for link in links if link.is_displayed()]
        return visible_links

    def get_nav_link_texts(self):
        return [link.text.strip().lower() for link in self.get_nav_links()]

@pytest.fixture(scope="function")
def driver():
    # Setup: Start browser
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    # Teardown: Quit browser
    driver.quit()

@pytest.mark.tc013
def test_tc013_navigation_bar_links_for_unauthenticated_users(driver):
    # Step 1: Ensure user is logged out (fresh browser, no cookies)
    driver.delete_all_cookies()

    # Step 2: Visit home/index page
    base_url = "http://localhost:5000/"  # Adjust if needed
    driver.get(base_url)

    # Step 3: Observe navigation bar and check available links
    nav_bar = NavigationBar(driver)
    # Wait for at least one nav link to be visible
    WebDriverWait(driver, 10).until(
        lambda d: len(nav_bar.get_nav_links()) > 0
    )

    nav_link_texts = nav_bar.get_nav_link_texts()

    # Expected links for unauthenticated users
    expected_links = {"login", "register", "problems"}
    # Restricted links (e.g., "add problem", "profile", "logout", etc.)
    restricted_links = {"add problem", "profile", "logout", "delete", "protected"}

    # Step 4: Assert only allowed links are visible
    for link in expected_links:
        assert link in nav_link_texts, f"Expected link '{link}' not visible for unauthenticated user."

    for link in restricted_links:
        assert link not in nav_link_texts, f"Restricted link '{link}' should not be visible for unauthenticated user."