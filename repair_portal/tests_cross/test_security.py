import time

from repair_portal.core import security


def test_require_roles_no_frappe_allows_execution(monkeypatch):
    monkeypatch.setattr(security, "frappe", None, raising=False)

    @security.require_roles("Technician")
    def sample() -> str:
        return "ok"

    assert sample() == "ok"


def test_rate_limited_without_frappe(monkeypatch):
    monkeypatch.setattr(security, "frappe", None, raising=False)

    calls = []

    @security.rate_limited("demo", limit=1, window_seconds=1)
    def sample() -> str:
        calls.append(time.time())
        return "ok"

    assert sample() == "ok"
    assert sample() == "ok"
    assert len(calls) == 2
