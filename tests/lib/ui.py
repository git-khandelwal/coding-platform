from __future__ import annotations

from playwright.sync_api import Page

from tests.lib.http import join_url


def accept_dialogs(page: Page) -> None:
    page.on("dialog", lambda d: d.accept())


def login_and_get_token(page: Page, base_url: str, user_credentials: dict) -> str:
    page.goto(base_url)
    accept_dialogs(page)

    page.locator("#login-username").fill(user_credentials["username"])
    page.locator("#login-password").fill(user_credentials["password"])
    page.locator("#login-form").get_by_role("button", name="Login").click()

    page.wait_for_timeout(500)
    token = page.evaluate("() => localStorage.getItem('token')")
    assert token, "Expected JWT token in localStorage after login"
    return token


def goto_add_problem(page: Page, base_url: str) -> None:
    page.goto(join_url(base_url, "/problems/add"))
    page.wait_for_load_state("networkidle")

