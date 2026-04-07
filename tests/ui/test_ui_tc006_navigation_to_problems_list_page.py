import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from playwright.sync_api import sync_playwright, Page, BrowserContext

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def playwright_context() -> BrowserContext:
    """
    Launches a Playwright Chromium browser with remote debugging enabled.
    Returns the browser context and the first page.
    """
    with sync_playwright() as p:
        # Launch Chromium with a fixed remote debugging port
        browser = p.chromium.launch(
            headless=False,
            args=["--remote-debugging-port=9222"]
        )
        context = browser.new_context()
        page = context.new_page()
        yield context, page
        context.close()
        browser.close()


@pytest.fixture(scope="session")
def selenium_driver(playwright_context) -> webdriver.Chrome:
    """
    Connects Selenium to the Playwright launched Chromium instance via
    the remote debugging port.
    """
    # Selenium ChromeOptions to attach to the existing Chrome instance
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


class HomePage:
    """
    Page Object for the Home Page.
    """
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def load(self):
        self.driver.get(BASE_URL)

    def click_problems_link(self):
        problems_link = self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Problems"))
        )
        problems_link.click()


class ProblemsPage:
    """
    Page Object for the Problems List Page.
    """
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def is_loaded(self) -> bool:
        # Wait until the title is "Problems" and the URL