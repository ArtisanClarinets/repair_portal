"""Seed Opportunity Type pipelines for school CRM flows."""
from __future__ import annotations

from typing import Iterable

import frappe

PIPELINES: tuple[dict[str, Iterable[str]], ...] = (
    {
        "name": "School Service Program",
        "stages": (
            "Inquiry",
            "Needs Analysis",
            "Proposal Sent",
            "Awaiting Purchase Order",
            "Won",
            "Lost",
        ),
    },
    {
        "name": "Instrument Rental Fleet",
        "stages": (
            "Requested",
            "Scheduling Demo",
            "Trial In Progress",
            "Agreement Drafted",
            "Won",
            "Lost",
        ),
    },
    {
        "name": "Clarinet Overhaul",
        "stages": (
            "Lead",
            "Evaluation",
            "Quote Delivered",
            "Approval Pending",
            "Won",
            "Lost",
        ),
    },
)


def execute() -> None:
    if not frappe.db.table_exists("tabOpportunity Type"):
        return
    for pipeline in PIPELINES:
        ensure_opportunity_type(pipeline["name"], tuple(pipeline["stages"]))


def ensure_opportunity_type(name: str, stages: tuple[str, ...]) -> None:
    existing = frappe.db.exists("Opportunity Type", {"opportunity_type": name})
    if existing:
        doc = frappe.get_doc("Opportunity Type", existing)
    else:
        doc = frappe.get_doc({"doctype": "Opportunity Type", "opportunity_type": name})
    doc.flags.ignore_permissions = True
    desired = list(stages)
    if not desired:
        return
    doc.set("stages", [])
    for idx, stage in enumerate(desired):
        doc.append(
            "stages",
            {
                "stage_name": stage,
                "probability": stage_probability(stage, idx, len(desired)),
            },
        )
    if existing:
        doc.save()
    else:
        doc.insert()


def stage_probability(stage: str, position: int, total: int) -> int:
    lowered = stage.lower()
    if lowered == "won":
        return 100
    if lowered == "lost":
        return 0
    if total <= 2:
        return 50
    step = max(100 // max(total - 2, 1), 10)
    return min(90, step * (position + 1))
