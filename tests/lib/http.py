from __future__ import annotations


def join_url(base_url: str, path: str) -> str:
    base = (base_url or "").rstrip("/")
    if not path:
        return base
    if not path.startswith("/"):
        path = "/" + path
    return base + path

