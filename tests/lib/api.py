from __future__ import annotations

from typing import Any, Mapping

from tests.lib.http import join_url


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def get_problem(
    client: Any,
    base_url: str,
    problem_id: int,
    headers: Mapping[str, str] | None = None,
) -> dict:
    url = join_url(base_url, f"/problems/{problem_id}")
    resp = client.get(url, headers=headers)
    assert resp.status_code == 200, f"Failed to retrieve problem {problem_id}"
    return resp.json()

