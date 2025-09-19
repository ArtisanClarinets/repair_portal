# -*- coding: utf-8 -*-
"""
Path: repair_portal/repair/services/sla.py
Version: 1.0.2
Purpose:
    SLA engine for Repair Orders (RO):
      - Applies SLA when a RO enters a configured "start" workflow state
      - Computes due-by, live progress %, traffic-light status (Green/Yellow/Red)
      - Detects breach with grace window and sends idempotent escalations by role
      - Keeps status fresh on any RO update, and via a 10-min scheduled sweep

Public API:
    - apply_sla_on_event(ro_name: str, event: str) -> None
    - recompute_sla(ro_name: str) -> None
    - sweep_breaches_and_escalate() -> None

Hook entry:
    - handle_ro_update(doc, method) -> None  # wire in hooks.py: on_update of Repair Order

Notes / Requirements:
    - Requires DocTypes:
        * "SLA Policy" (master) with child table "SLA Policy Rule"
        * Repair Order has fields: sla_policy (Link), sla_start (Datetime),
          sla_due (Datetime), sla_progress_pct (Percent), sla_status (Select),
          sla_breached (Check)
    - Expected workflow_state labels on RO for matching:
        START: {"Intake Received", "Estimate Approved", "Work Started"}
        STOP : {"Ready for QA", "Delivered"}
    - Escalations are idempotent per level using Communication.subject matching:
        "SLA Escalation L1: <RO-NAME>", "SLA Escalation L2: <RO-NAME>"
"""

from __future__ import annotations

from typing import Optional, List

import frappe
from frappe.utils import add_to_date, now_datetime, flt, get_url_to_form
from frappe.utils.jinja import render_template

# -----------------------------
# Configuration & Constants
# -----------------------------

START_EVENTS = {"Intake Received", "Estimate Approved", "Work Started"}
STOP_EVENTS = {"Ready for QA", "Delivered"}

STATUS_NONE = "None"
STATUS_GREEN = "Green"
STATUS_YELLOW = "Yellow"
STATUS_RED = "Red"

# Email template for escalations (optional; we fall back to plain HTML if missing)
ESCALATION_TEMPLATE = "repair_portal/templates/emails/sla_escalation.html"

# Field names on Repair Order (kept here to avoid typos)
RO_FIELD_SLA_POLICY = "sla_policy"
RO_FIELD_SLA_START = "sla_start"
RO_FIELD_SLA_DUE = "sla_due"
RO_FIELD_SLA_PCT = "sla_progress_pct"
RO_FIELD_SLA_STATUS = "sla_status"
RO_FIELD_SLA_BREACHED = "sla_breached"

# Small cache TTL (in-memory) to avoid repeated policy lookups within a single request
# (frappe.local.request_id scope). Not persisted.
_policy_cache: dict[str, frappe._dict] = {}


# -----------------------------
# Hook entry
# -----------------------------
def handle_ro_update(doc, method=None):
    """Hook: called on Repair Order on_update.

    - Detect workflow_state transitions into known START/STOP events
    - Apply or recompute SLA accordingly
    - Keep status fresh on any update while SLA is active
    """
    if doc.doctype != "Repair Order":
        return

    try:
        prev_state = frappe.db.get_value("Repair Order", doc.name, "workflow_state")
        cur_state = (doc.workflow_state or "").strip()

        if cur_state and cur_state != (prev_state or ""):
            if cur_state in START_EVENTS:
                apply_sla_on_event(doc.name, cur_state)
            elif cur_state in STOP_EVENTS:
                # Recompute on stop events to freeze final status/breach state
                recompute_sla(doc.name)
        else:
            # On any other update, keep progress fresh if SLA already started
            if doc.get(RO_FIELD_SLA_START):
                recompute_sla(doc.name)
    except Exception:
        _log().exception("SLA handle_ro_update failed for %s", doc.name)
        # Never block the save; SLA is advisory
        frappe.clear_last_message()


# -----------------------------
# Core SLA public functions
# -----------------------------
def apply_sla_on_event(ro_name: str, event: str) -> None:
    """If the event is a starting event for a matching rule, set sla_start/sla_due and recompute."""
    ro = frappe.get_doc("Repair Order", ro_name)
    policy = _get_policy_for_ro(ro)
    if not policy or not _event_is_start(event):
        return

    rule = _pick_rule(policy, ro, event, for_start=True)
    if not rule:
        return

    # Set start once (idempotent)
    if not ro.get(RO_FIELD_SLA_START):
        ro.db_set(RO_FIELD_SLA_START, now_datetime())

    # Compute due
    tat_hours = int(rule.tat_hours or 0)
    if tat_hours <= 0:
        # If rule is malformed, don't proceed
        _log().warning("SLA rule with non-positive TAT for RO %s; skipping.", ro.name)
        return

    due = add_to_date(ro.get(RO_FIELD_SLA_START), hours=tat_hours)
    ro.db_set(RO_FIELD_SLA_DUE, due)

    # Attach policy (so we know which policy applied)
    if ro.get(RO_FIELD_SLA_POLICY) != policy.name:
        ro.db_set(RO_FIELD_SLA_POLICY, policy.name)

    # Initial compute
    recompute_sla(ro.name)


def recompute_sla(ro_name: str) -> None:
    """Update progress %, status color, and breach flag based on policy thresholds."""
    ro = frappe.get_doc("Repair Order", ro_name)
    policy = _get_policy_for_ro(ro)
    if not policy:
        # Clear SLA fields if no policy found
        _reset_sla_fields(ro)
        return

    if not ro.get(RO_FIELD_SLA_START) or not ro.get(RO_FIELD_SLA_DUE):
        return

    now = now_datetime()
    start = ro.get(RO_FIELD_SLA_START)
    due = ro.get(RO_FIELD_SLA_DUE)

    total_secs = max(1, (due - start).total_seconds())
    elapsed_secs = max(0, (now - start).total_seconds())
    pct = min(100.0, max(0.0, (elapsed_secs / total_secs) * 100.0))

    status = STATUS_GREEN
    warn = int(policy.warn_threshold_pct or 70)
    crit = int(policy.critical_threshold_pct or 90)
    if pct >= crit:
        status = STATUS_RED
    elif pct >= warn:
        status = STATUS_YELLOW

    grace = int(policy.breach_grace_minutes or 0)
    breached = 1 if (now > add_to_date(due, minutes=grace)) else 0

    # Single transaction: set all fields without triggering recursion
    ro.db_set(RO_FIELD_SLA_PCT, flt(pct, 2), update_modified=False)
    ro.db_set(RO_FIELD_SLA_STATUS, status, update_modified=False)
    ro.db_set(RO_FIELD_SLA_BREACHED, breached, update_modified=False)
    frappe.db.set_value("Repair Order", ro.name, "modified", now, update_modified=False)


def sweep_breaches_and_escalate() -> None:
    """Cron: find overdue ROs and send escalations per matching rule thresholds."""
    # Pull candidates that have a due time, not cancelled/archived.
    # Add extra filters as your business rules dictate (e.g., exclude Delivered).
    ros = frappe.get_all(
        "Repair Order",
        filters={
            RO_FIELD_SLA_DUE: ["is", "set"],
            "docstatus": ["<", 2],
        },
        fields=[
            "name",
            RO_FIELD_SLA_POLICY,
            RO_FIELD_SLA_START,
            RO_FIELD_SLA_DUE,
            RO_FIELD_SLA_BREACHED,
            "workflow_state",
            "workshop",
            "service_type",
            "customer",
            "customer_name",
        ],
        order_by=f"{RO_FIELD_SLA_DUE} asc",
    )

    for row in ros:
        try:
            ro = frappe.get_doc("Repair Order", row.name)
            policy = _get_policy_for_ro(ro)
            if not policy:
                continue

            # Always recompute first (keeps pct/status in sync)
            recompute_sla(ro.name)

            if not ro.get(RO_FIELD_SLA_BREACHED):
                continue

            # Find the rule that started this SLA (best-effort)
            start_event = _infer_start_event(ro)
            rule = _pick_rule(policy, ro, start_event, for_start=True)
            if not rule:
                continue

            _maybe_escalate(ro, rule, level=1)
            _maybe_escalate(ro, rule, level=2)
        except Exception:
            _log().exception("SLA sweep failed for Repair Order %s", row.name)
            frappe.clear_last_message()


# -----------------------------
# Helpers
# -----------------------------
def _get_policy_for_ro(ro) -> Optional[frappe._dict]:
    """Return explicit policy (if set on RO) or the enabled default policy."""
    # Try cached
    key = ro.get(RO_FIELD_SLA_POLICY) or "__default__"
    cached = _policy_cache.get(key)
    if cached:
        return cached

    # Explicit policy on RO
    if ro.get(RO_FIELD_SLA_POLICY):
        try:
            doc = frappe.get_doc("SLA Policy", ro.get(RO_FIELD_SLA_POLICY))
            _policy_cache[key] = doc
            return doc
        except frappe.DoesNotExistError:
            pass

    # Fallback to enabled default
    res = frappe.get_all(
        "SLA Policy",
        filters={"enabled": 1, "default_policy": 1},
        fields=[
            "name",
            "apply_per_workshop",
            "breach_grace_minutes",
            "warn_threshold_pct",
            "critical_threshold_pct",
        ],
        limit=1,
    )
    if res:
        doc = frappe.get_doc("SLA Policy", res[0].name)
        _policy_cache["__default__"] = doc
        return doc
    return None


def _event_is_start(event: str) -> bool:
    return (event or "") in START_EVENTS


def _event_is_stop(event: str) -> bool:
    return (event or "") in STOP_EVENTS


def _pick_rule(policy, ro, event: str, for_start: bool) -> Optional[frappe._dict]:
    """Select the best matching rule for this RO and event.

    Priority:
      1) Exact service_type + exact workshop (if apply_per_workshop)
      2) Exact service_type + workshop is empty
      3) service_type empty + exact workshop (if apply_per_workshop)
      4) service_type empty + workshop empty
    """
    service_type = ro.get("service_type") or ro.get("repair_type") or ro.get("service_category")
    workshop = ro.get("workshop")
    want_field = "start_event" if for_start else "stop_event"

    rules = policy.get("rules") or []

    def match_score(r) -> int:
        score = 0
        if getattr(r, want_field, None) == event:
            score += 8
        if service_type and r.service_type == service_type:
            score += 4
        elif not r.service_type:
            score += 1
        if getattr(policy, "apply_per_workshop", 0):
            if workshop and r.workshop == workshop:
                score += 2
            elif not r.workshop:
                score += 1
        else:
            score += 1  # workshop not considered
        return score

    best = None
    best_score = -1
    for r in rules:
        if getattr(r, want_field, None) != event:
            continue
        sc = match_score(r)
        if sc > best_score:
            best, best_score = r, sc
    return best


def _reset_sla_fields(ro):
    # Reset all SLA fields (no policy matched / disabled)
    ro.db_set(RO_FIELD_SLA_POLICY, None, update_modified=False)
    ro.db_set(RO_FIELD_SLA_START, None, update_modified=False)
    ro.db_set(RO_FIELD_SLA_DUE, None, update_modified=False)
    ro.db_set(RO_FIELD_SLA_PCT, 0, update_modified=False)
    ro.db_set(RO_FIELD_SLA_STATUS, STATUS_NONE, update_modified=False)
    ro.db_set(RO_FIELD_SLA_BREACHED, 0, update_modified=False)


def _infer_start_event(ro) -> str:
    """Best guess: use current workflow_state if it's a START event,
    else fall back in order of preference."""
    state = (ro.get("workflow_state") or "").strip()
    if state in START_EVENTS:
        return state
    # Fallback preference order
    for ev in ("Work Started", "Estimate Approved", "Intake Received"):
        if ev in START_EVENTS:
            return ev
    return "Work Started"


def _maybe_escalate(ro, rule, level: int):
    """Send one escalation per level once the overdue time passes the threshold."""
    minutes_overdue = _minutes_overdue(ro)
    if minutes_overdue is None:
        return

    if level == 1:
        threshold = int(rule.escalation_minutes_1 or 0)
        role = rule.escalate_to_role_1
        level_tag = "L1"
    else:
        threshold = int(rule.escalation_minutes_2 or 0)
        role = rule.escalate_to_role_2
        level_tag = "L2"

    if threshold <= 0 or minutes_overdue < threshold or not role:
        return

    subject = f"SLA Escalation {level_tag}: {ro.name}"

    # Idempotency: avoid duplicate Communications for the same level
    already = frappe.get_all(
        "Communication",
        filters={
            "reference_doctype": "Repair Order",
            "reference_name": ro.name,
            "subject": subject,
        },
        limit=1,
    )
    if already:
        return

    recipients = _users_with_role(role)
    if not recipients:
        _log().warning("No active users found for role '%s' (RO %s) during SLA escalation.", role, ro.name)
        return

    link = get_url_to_form("Repair Order", ro.name)
    body = _render_escalation_body(
        ro=ro,
        overdue_minutes=minutes_overdue,
        level_tag=level_tag,
        link=link,
    )

    try:
        frappe.sendmail(
            recipients=recipients,
            subject=subject,
            message=body,
            reference_doctype="Repair Order",
            reference_name=ro.name,
        )
    except Exception:
        # Don't crash the sweep; log and continue
        _log().exception("Failed to send SLA escalation email for %s (%s)", ro.name, level_tag)
        frappe.clear_last_message()


def _render_escalation_body(ro, overdue_minutes: int, level_tag: str, link: str) -> str:
    """Render escalation email body using the HTML template if present; fallback to simple HTML."""
    ctx = {
        "ro": ro.as_dict(),
        "overdue_minutes": overdue_minutes,
        "level_tag": level_tag,
        "link": link,
        "frappe": frappe,
    }
    try:
        # Will raise TemplateNotFound if missing
        return render_template(ESCALATION_TEMPLATE, ctx)
    except Exception:
        # Fallback body: minimal, safe, no template dependency
        return (
            f"<h3>SLA Escalation {level_tag}</h3>"
            f"<p>Repair Order <b>{frappe.utils.escape_html(ro.name)}</b> "
            f"is overdue by <b>{overdue_minutes} minutes</b> against SLA.</p>"
            f"<p><b>Customer:</b> {frappe.utils.escape_html(ro.get('customer_name') or ro.get('customer') or '-')}</p>"
            f"<p><b>Workshop:</b> {frappe.utils.escape_html(ro.get('workshop') or '-')}<br>"
            f"<b>Service Type:</b> {frappe.utils.escape_html(ro.get('service_type') or '-')}</p>"
            f"<p><a href='{frappe.utils.escape_html(link)}'>Open Repair Order</a></p>"
        )


def _minutes_overdue(ro) -> Optional[int]:
    """Return minutes overdue (integer) or None if not yet overdue."""
    due = ro.get(RO_FIELD_SLA_DUE)
    if not due:
        return None
    now = now_datetime()
    delta = now - due
    if delta.total_seconds() <= 0:
        return None
    return int(delta.total_seconds() // 60)


def _users_with_role(role: str) -> List[str]:
    """Return enabled user IDs having the given Role."""
    rows = frappe.get_all("Has Role", filters={"role": role}, fields=["parent as user"])
    users = [r.user for r in rows] if rows else []
    if not users:
        return []
    active = frappe.get_all("User", filters={"name": ["in", users], "enabled": 1}, pluck="name")
    return active or []


def _log():
    return frappe.logger("repair_portal.sla", allow_site=True)
