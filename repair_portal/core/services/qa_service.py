"""QA service helpers."""

from __future__ import annotations

from typing import Mapping

from ..contracts import qa as qa_contracts
from ..events import publish
from ..registry import EventTopic, Role
from ..security import rate_limited, require_roles

try:
    import frappe
except ImportError:  # pragma: no cover - integration tests handle skip
    frappe = None  # type: ignore

LOGGER_NAME = "repair_portal.qa"


def _log(message: str, **context: object) -> None:
    if frappe is not None:
        frappe.logger(LOGGER_NAME).info(message, **context)


@require_roles(Role.QA, Role.REPAIR_MANAGER)
@rate_limited("qa-record", limit=120, window_seconds=60)
def record_outcome(payload: Mapping[str, object]) -> qa_contracts.QAOutcome:
    """Persist a QA outcome and emit matching events."""

    outcome = qa_contracts.QAOutcome(**payload)
    _log("QA outcome recorded", repair_order=outcome.repair_order, passed=outcome.passed)
    if frappe is not None:
        doc = frappe.get_doc(
            {
                "doctype": "Repair QA Outcome",
                "repair_order": outcome.repair_order,
                "passed": outcome.passed,
                "inspected_by": outcome.inspected_by,
                "inspected_at": outcome.inspected_at,
                "notes": outcome.notes,
            }
        )
        doc.flags.ignore_permissions = True
        doc.save()
        frappe.db.set_value(
            "Repair Order",
            outcome.repair_order,
            {
                "qa_status": "Passed" if outcome.passed else "Failed",
                "qa_completed_on": outcome.inspected_at,
            },
        )
    publish(
        EventTopic.QA_PASSED if outcome.passed else EventTopic.QA_FAILED,
        outcome.dict(),
    )
    return outcome


@require_roles(Role.QA, Role.REPAIR_MANAGER)
@rate_limited("qa-reopen", limit=60, window_seconds=60)
def reopen_after_failure(repair_order: str, reason: str) -> None:
    """Reopen an order after QA failure."""

    _log("QA reopen", repair_order=repair_order, reason=reason)
    if frappe is not None:
        frappe.db.set_value(
            "Repair Order",
            repair_order,
            {
                "workflow_state": "In Progress",
                "qa_status": "Failed",
                "qa_notes": reason,
            },
        )
    publish(EventTopic.QA_FAILED, {"repair_order": repair_order, "reason": reason})


def latest_outcome(repair_order: str) -> qa_contracts.QAOutcome | None:
    """Return the latest QA outcome for a repair order."""

    if frappe is None:
        return None
    record = frappe.db.get_value(
        "Repair QA Outcome",
        {"repair_order": repair_order},
        ["repair_order", "passed", "inspected_by", "inspected_at", "notes"],
        as_dict=True,
        order_by="modified desc",
    )
    if not record:
        return None
    return qa_contracts.QAOutcome(
        repair_order=record["repair_order"],
        passed=record["passed"],
        inspected_by=record["inspected_by"],
        inspected_at=record["inspected_at"],
        checklist=qa_contracts.QAChecklistRef(template="unknown"),
        notes=record.get("notes"),
    )
