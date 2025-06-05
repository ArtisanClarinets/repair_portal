import sys
import types

import pytest


def test_cleanup_run(monkeypatch):
    calls = {"get_all": 0, "delete_doc": 0, "commit": 0}

    def fake_get_all(doctype, filters=None):
        calls["get_all"] += 1
        return [types.SimpleNamespace(name="TestDoc")]

    def fake_delete_doc(doctype, name, force=True):
        calls["delete_doc"] += 1

    def fake_commit():
        calls["commit"] += 1

    fake_frappe = types.SimpleNamespace(
        get_all=fake_get_all,
        delete_doc=fake_delete_doc,
        db=types.SimpleNamespace(commit=fake_commit),
    )

    monkeypatch.setitem(sys.modules, "frappe", fake_frappe)

    from repair_portal.utils import cleanup_repair_apps

    cleanup_repair_apps.run()

    assert calls["get_all"] > 0
    assert calls["delete_doc"] > 0
    assert calls["commit"] == 1
