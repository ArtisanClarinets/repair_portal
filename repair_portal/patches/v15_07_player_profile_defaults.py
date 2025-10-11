"""Seed Player Profile naming series and email group."""

from __future__ import annotations

import frappe

PLAYER_NEWSLETTER = "Player Newsletter"


def execute() -> None:
    _ensure_email_group()
    _ensure_player_series()


def _ensure_email_group() -> None:
    if frappe.db.exists("Email Group", PLAYER_NEWSLETTER):
        return
    doc = frappe.get_doc({
        "doctype": "Email Group",
        "title": PLAYER_NEWSLETTER,
    })
    doc.insert(ignore_permissions=True)


def _ensure_player_series() -> None:
    if frappe.db.exists("Series", "PLAYER-"):
        return
    frappe.db.sql(  # nosec B608 - parameterised insert into Series table
        "INSERT INTO `tabSeries` (name, current) VALUES (%s, %s)",
        ("PLAYER-", 0),
    )
