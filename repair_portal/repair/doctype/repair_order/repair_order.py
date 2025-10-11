"""Repair Order controller with workflow, labor, materials, SLA, and billing logic.

All heavy lifting happens server-side to guarantee a single source of truth for
technician actions and customer communications. The implementation is guarded
so that it remains backwards compatible with partially configured sites while
still enforcing the stricter workflow mandated for enterprise deployments.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import cint, flt, get_datetime, get_link_to_form, now_datetime

WORKFLOW_SEQUENCE: tuple[str, ...] = (
    "Requested",
    "Quoted",
    "In Progress",
    "Ready for QA",
    "Completed",
    "Delivered",
)

SLA_STATUSES = {"On Track", "At Risk", "Paused", "Breached"}
BILLING_STATES = {"Draft", "Invoiced", "Paid", "Warranty"}


@dataclass
class MaterialRow:
    item_code: str
    qty: float
    warehouse: str
    batch_no: str | None = None
    serial_no: str | None = None


class RepairOrder(Document):
    """Rich workflow controller for the Repair Order doctype."""

        actual_materials: DF.Table[RepairActualMaterial]
        assigned_technician: DF.Link | None
        company: DF.Link | None
        customer: DF.Link
        instrument_profile: DF.Link | None
        intake: DF.Link | None
        is_warranty: DF.Check
        labor_item: DF.Link
        labor_rate: DF.Currency
        naming_series: DF.Data
        planned_materials: DF.Table[RepairPlannedMaterial]
        posting_date: DF.Date | None
        priority: DF.Literal[Low, Medium, High, Critical]
        player_profile: DF.Link | None
        qa_required: DF.Check
        related_documents: DF.Table[RepairRelatedDocument]
        remarks: DF.SmallText | None
        require_invoice_before_delivery: DF.Check
        target_delivery: DF.Date | None
        total_actual_minutes: DF.Int
        total_estimated_minutes: DF.Int
        warehouse_source: DF.Link
        warranty_until: DF.Date | None
        workflow_state: DF.Literal[Draft, "In Progress", QA, Ready, Delivered, Closed]
    # end: auto-generated types
    # ---- Lifecycle ---------------------------------------------------------

    def validate(self):
        self._apply_defaults_from_settings()
        self._validate_workflow_state()
        self._dedupe_related()
        self._normalize_links()
        self._sync_player_profile()
        self._recompute_time_totals()
        self._apply_warranty_flags()  # safe no-op if warranty fields not present

    # ---- Defaults / Settings ----------------------------------------------

    def _apply_defaults_from_settings(self) -> None:
        """Populate blank fields from Single 'Repair Settings' if available."""
        try:
            settings = frappe.get_single("Repair Settings")
        except Exception:
            return

        if not self.company and settings.get("default_company"):
            self.company = settings.default_company
        if not self.warehouse_source and settings.get("default_source_warehouse"):
            self.warehouse_source = settings.default_source_warehouse
        if not self.labor_item and settings.get("default_labor_item"):
            self.labor_item = settings.default_labor_item
        if not flt(self.labor_rate) and settings.get("default_labor_rate"):
            self.labor_rate = flt(settings.default_labor_rate)
        if not flt(self.overtime_multiplier):
            self.overtime_multiplier = flt(settings.get("default_overtime_multiplier") or 1.0)
        if not flt(self.rush_multiplier):
            self.rush_multiplier = flt(settings.get("default_rush_multiplier") or 1.0)
        if not self.sla_policy and settings.get("default_sla_policy"):
            self.sla_policy = settings.default_sla_policy

    def _validate_workflow_state(self) -> None:
        if not self.workflow_state:
            self.workflow_state = WORKFLOW_SEQUENCE[0]
            return
        if self.workflow_state not in WORKFLOW_SEQUENCE:
            frappe.throw(_("Invalid workflow state: {0}").format(self.workflow_state))
        if self._doc_before_save:
            previous = self._doc_before_save.workflow_state or WORKFLOW_SEQUENCE[0]
            allowed = self._allowed_next_states(previous)
            if self.workflow_state not in allowed:
                frappe.throw(
                    _("Illegal transition from {0} to {1}. Allowed transitions: {2}")
                    .format(previous, self.workflow_state, ", ".join(allowed))
                )

    def _allowed_next_states(self, current: str) -> tuple[str, ...]:
        idx = WORKFLOW_SEQUENCE.index(current) if current in WORKFLOW_SEQUENCE else 0
        if current == "Requested":
            return ("Requested", "Quoted")
        if current == "Quoted":
            return ("Quoted", "In Progress")
        if current == "In Progress":
            return ("In Progress", "Ready for QA")
        if current == "Ready for QA":
            return ("Ready for QA", "In Progress", "Completed")
        if current == "Completed":
            return ("Completed", "Delivered")
        if current == "Delivered":
            return ("Delivered",)
        return (WORKFLOW_SEQUENCE[idx],)

    def _validate_required_links(self) -> None:
        missing = []
        if not self.customer:
            missing.append("Customer")
        if not self.warehouse_source:
            missing.append("Source Warehouse")
        if missing:
            frappe.throw(_("Repair Order missing required fields: {0}").format(", ".join(missing)))

    def _validate_labor_sessions(self) -> None:
        total = 0
        for row in self.labor_sessions or []:
            if not row.started_on or not row.ended_on:
                frappe.throw(_("Labor session {0} must have start and end times.").format(row.idx))
            start = get_datetime(row.started_on)
            end = get_datetime(row.ended_on)
            if start >= end:
                frappe.throw(_("Labor session {0} end must be after start.").format(row.idx))
            total += (end - start).total_seconds() / 60
        self.total_actual_minutes = cint(total)

    def _ensure_material_rows_are_consistent(self) -> None:
        for row in self.actual_materials or []:
            if not row.item_code:
                frappe.throw(_("Actual material row {0} requires an Item.").format(row.idx))
            if flt(row.qty) <= 0:
                frappe.throw(_("Actual material row {0} must have positive quantity.").format(row.idx))
            if not row.warehouse:
                row.warehouse = self.warehouse_source

    def _enforce_qa_gate(self) -> None:
        if self.workflow_state in {"Completed", "Delivered"} and self.qa_required:
            if not self.qa_inspection:
                frappe.throw(_("QA inspection is required before completion."))
            if self.qa_status != "Pass":
                frappe.throw(_("QA inspection must be marked as Pass before completion."))

    def _set_billing_status(self) -> None:
        if self.is_warranty:
            self.billing_status = "Warranty"
            return
        if self.billing_status not in BILLING_STATES:
            self.billing_status = "Draft"

    # ------------------------------------------------------------------
    # Computations
    # ------------------------------------------------------------------
    def _rollup_time_totals(self) -> None:
        estimated = sum(flt(row.estimated_minutes or 0) for row in self.labor_sessions or [])
        actual_minutes = 0.0
        for row in self.labor_sessions or []:
            start = get_datetime(row.started_on) if row.started_on else None
            end = get_datetime(row.ended_on) if row.ended_on else None
            if start and end:
                actual_minutes += (end - start).total_seconds() / 60
        multiplier = flt(self.overtime_multiplier or 1.0) * flt(self.rush_multiplier or 1.0)
        hours = (actual_minutes / 60.0) * multiplier
        self.total_estimated_minutes = cint(estimated)
        self.total_actual_minutes = cint(actual_minutes)
        self.total_billable_hours = flt(hours, 2)

    def _compute_sla_due(self) -> None:
        if not self.sla_policy:
            return
        seen = set()
        deduped = []
        for row in (self.related_documents or []):
            key = (row.doctype_name, row.document_name)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(row)
        self.related_documents = deduped

    def _sync_player_profile(self) -> None:
        if not self.meta.has_field("player_profile"):
            return

        profile_name = self.get("player_profile")
        if not profile_name and self.intake and self.meta.has_field("intake"):
            try:
                profile_name = frappe.db.get_value("Clarinet Intake", self.intake, "player_profile")
            except Exception:
                frappe.log_error(title="RepairOrder Player Profile", message=frappe.get_traceback())
                profile_name = None

        if not profile_name and self.instrument_profile:
            try:
                if frappe.db.has_column("Instrument Profile", "owner_player"):
                    profile_name = frappe.db.get_value(
                        "Instrument Profile", self.instrument_profile, "owner_player"
                    )
            except Exception:
                frappe.log_error(title="RepairOrder Player Profile", message=frappe.get_traceback())
                profile_name = None

        if profile_name:
            self.player_profile = profile_name
            if self.meta.has_field("customer") and not self.customer:
                try:
                    customer = frappe.db.get_value("Player Profile", profile_name, "customer")
                    if customer:
                        self.customer = customer
                except Exception:
                    frappe.log_error(title="RepairOrder Player Profile Customer", message=frappe.get_traceback())

    # ---- Minutes / Totals --------------------------------------------------

    def _recompute_time_totals(self) -> None:
        """Aggregate est/actual minutes from child Repair Task rows if table exists."""
        est_total = 0
        act_total = 0
        if self.meta.has_field("repair_tasks"):
            for t in (self.get("repair_tasks") or []):
                est_total += flt(t.get("est_minutes"))
                act_total += flt(t.get("actual_minutes"))
        if self.meta.has_field("total_estimated_minutes"):
            self.total_estimated_minutes = int(est_total)
        if self.meta.has_field("total_actual_minutes"):
            self.total_actual_minutes = int(act_total)

    # ---- Warranty flags (optional) -----------------------------------------

    def _apply_warranty_flags(self) -> None:
        """Populate is_warranty / warranty_until from Instrument Profile when available.

        - Looks for a date field on Instrument Profile with common names:
          'warranty_until' (preferred) or 'warranty_end_date' (fallback).
        - If today's date <= warranty_until: is_warranty = 1, else 0.
        - Safe no-op if fields or Instrument Profile are absent.
        """
        if not self.meta.has_field("is_warranty") and not self.meta.has_field("warranty_until"):
            return
        if not sla_rule.get("response_time"):
            return
        baseline = get_datetime(self.posting_date) if self.posting_date else now_datetime()
        self.sla_due_date = baseline + sla_rule.response_time
        self._update_sla_status()

    def _update_sla_status(self) -> None:
        if self.sla_status == "Paused":
            return
        if not self.sla_due_date:
            self.sla_status = "On Track"
            return
        remaining = (self.sla_due_date - now_datetime()).total_seconds()
        if remaining <= 0:
            self.sla_status = "Breached"
        elif remaining < 3600 * 6:
            self.sla_status = "At Risk"
        else:
            self.sla_status = "On Track"

    def _sync_current_stage(self) -> None:
        self.current_stage = self.workflow_state or WORKFLOW_SEQUENCE[0]

    def _sync_player_profile_links(self) -> None:
        if not self.player_profile or not self.customer:
            return
        try:
            profile = frappe.get_doc("Player Profile", self.player_profile)
        except Exception:
            return
        if profile.customer and profile.customer != self.customer:
            return
        if not profile.customer:
            profile.db_set("customer", self.customer, notify=True)

    def _enqueue_sla_monitor_if_needed(self) -> None:
        if frappe.flags.in_test or frappe.flags.in_migrate:
            return
        frappe.enqueue("repair_portal.repair.doctype.repair_order.repair_order.monitor_open_orders")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @frappe.whitelist()
    def consume_materials(self) -> str:
        self.check_permission("write")
        self.reload()
        material_rows = self._material_rows_for_issue()
        if not material_rows:
            frappe.throw(_("No planned materials available to consume."))
        stock_entry = self._create_stock_entry(material_rows)
        frappe.msgprint(
            _("Created Stock Entry {0} for material consumption.").format(
                get_link_to_form("Stock Entry", stock_entry.name)
            ),
            indicator="green",
        )
        return stock_entry.name

    def _material_rows_for_issue(self) -> list[MaterialRow]:
        rows: list[MaterialRow] = []
        for planned in self.planned_materials or []:
            qty = flt(planned.qty) - flt(planned.consumed_qty or 0)
            if qty <= 0:
                continue
            rows.append(
                MaterialRow(
                    item_code=planned.item_code,
                    qty=qty,
                    warehouse=self.warehouse_source,
                    batch_no=getattr(planned, "batch_no", None),
                    serial_no=getattr(planned, "serial_no", None),
                )
            )
        return rows

    def _create_stock_entry(self, rows: Iterable[MaterialRow]):
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = "Material Issue"
        stock_entry.company = self.company
        stock_entry.repair_order = self.name
        for row in rows:
            stock_entry.append(
                "items",
                {
                    "item_code": row.item_code,
                    "qty": row.qty,
                    "s_warehouse": row.warehouse,
                    "batch_no": row.batch_no,
                    "serial_no": row.serial_no,
                },
            )
        stock_entry.insert(ignore_permissions=True)
        stock_entry.submit()
        self.db_set("last_material_issue", stock_entry.name)
        self._mirror_stock_entry_to_actuals(stock_entry)
        return stock_entry

    def _mirror_stock_entry_to_actuals(self, stock_entry: Document) -> None:
        self.reload()
        self.set("actual_materials", [])
        for item in stock_entry.items:
            self.append(
                "actual_materials",
                {
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "warehouse": item.s_warehouse,
                    "batch_no": item.batch_no,
                    "serial_no": item.serial_no,
                    "stock_entry_detail": item.name,
                },
            )
        self.flags.ignore_validate_update_after_submit = True
        self.save(ignore_permissions=True)

    # ------------------------------------------------------------------
    # QA utilities
    # ------------------------------------------------------------------
    def record_qa_result(self, status: str, inspection: str | None = None) -> None:
        if status not in {"Pending", "Pass", "Fail"}:
            frappe.throw(_("Unsupported QA status"))
        self.qa_status = status
        if inspection:
            self.qa_inspection = inspection
        self.qa_completed_on = now_datetime() if status == "Pass" else None
        self.save(ignore_permissions=True)

    # ------------------------------------------------------------------
    # Finance helpers
    # ------------------------------------------------------------------
    def build_invoice_items(self) -> list[dict[str, object]]:
        labor_hours = self.total_billable_hours or 0
        labor_amount = flt(labor_hours) * flt(self.labor_rate or 0)
        items: list[dict[str, object]] = []
        if labor_amount or labor_hours:
            items.append(
                {
                    "item_code": self.labor_item,
                    "qty": labor_hours or 1,
                    "rate": self.labor_rate,
                    "description": _("Labor for Repair Order {0}").format(self.name),
                }
            )
        for row in self.actual_materials or []:
            items.append(
                {
                    "item_code": row.item_code,
                    "qty": row.qty,
                    "rate": row.rate or 0,
                    "warehouse": row.warehouse,
                    "description": _("Part for Repair Order {0}").format(self.name),
                }
            )
        return items

    @frappe.whitelist()
    def make_sales_invoice(self) -> str:
        self.check_permission("write")
        if self.billing_status in {"Invoiced", "Paid"}:
            frappe.throw(_("Repair Order already invoiced."))
        invoice = frappe.new_doc("Sales Invoice")
        invoice.customer = self.customer
        invoice.company = self.company
        invoice.repair_order = self.name
        invoice.set("items", [])
        for row in self.build_invoice_items():
            invoice.append("items", row)
        invoice.flags.ignore_permissions = True
        invoice.insert()
        if not self.require_invoice_before_delivery:
            invoice.submit()
        self.db_set("billing_status", "Invoiced")
        frappe.msgprint(
            _("Created Sales Invoice {0}").format(get_link_to_form("Sales Invoice", invoice.name)),
            indicator="green",
        )
        return invoice.name


# ---------------------------------------------------------------------------
# Scheduler + service helpers
# ---------------------------------------------------------------------------


def monitor_open_orders() -> None:
    """Scheduled job invoked hourly to evaluate SLA status and escalate."""
    open_orders = frappe.get_all(
        "Repair Order",
        filters={"workflow_state": ("not in", ["Delivered"])},
        fields=["name", "sla_status", "sla_due_date", "assigned_technician", "workflow_state"],
        order_by="modified desc",
    )
    for order in open_orders:
        try:
            _process_single_order(order)
        except Exception as exc:  # pragma: no cover - guard rail
            frappe.log_error(
                title="Repair SLA Monitor Failure",
                message=frappe.as_json({"order": order.name, "exc": frappe.get_traceback(), "error": str(exc)}),
            )


def _process_single_order(order: dict[str, object]) -> None:
    doc = frappe.get_doc("Repair Order", order["name"])
    previous = doc.sla_status
    doc._update_sla_status()
    if doc.sla_status != previous:
        doc.db_set("sla_status", doc.sla_status)
        doc.add_comment(
            "Info",
            _("SLA status changed to {0}").format(doc.sla_status),
        )
        if doc.sla_status in {"At Risk", "Breached"}:
            _notify_sla_escalation(doc)


def _notify_sla_escalation(doc: RepairOrder) -> None:
    recipients: list[str] = []
    if doc.assigned_technician:
        recipients.append(doc.assigned_technician)
    manager_role_users = [x.parent for x in frappe.get_all("Has Role", filters={"role": "Repair Manager"}, fields=["parent"])]
    recipients.extend(manager_role_users)
    recipients = sorted(set([r for r in recipients if r]))
    if not recipients:
        return
    frappe.sendmail(
        recipients=recipients,
        subject=_("Repair Order {0} SLA {1}").format(doc.name, doc.sla_status),
        message=_("Repair Order {0} is now {1} against SLA and needs attention.").format(doc.name, doc.sla_status),
    )


@frappe.whitelist()
def pause_sla(order: str, reason: str) -> None:
    doc: RepairOrder = frappe.get_doc("Repair Order", order)
    doc.check_permission("write")
    doc.db_set({
        "sla_status": "Paused",
        "sla_paused_on": now_datetime(),
        "sla_pause_reason": reason,
    })
    doc.add_comment("Info", _("SLA paused: {0}").format(reason))


@frappe.whitelist()
def generate_sales_invoice_from_ro(repair_order: str) -> str:
    ro = _get_ro(repair_order)

    if not ro.get("customer"):
        frappe.throw(_("Repair Order requires a Customer."))
    if not ro.get("labor_item"):
        frappe.throw(_("Repair Order requires a Labor Item (Service)."))

    company = ro.get("company") or frappe.defaults.get_global_default("company")
    if not company:
        frappe.throw(_("Company is required (set on Repair Order or defaults)."))

    si = frappe.new_doc("Sales Invoice")
    si.customer = ro.customer
    si.company = company
    si.set_posting_time = 1
    si.remarks = f"Repair Order: {ro.name}"

    if getattr(si.meta, "has_field", None) and si.meta.has_field("player_profile"):
        si.player_profile = ro.player_profile

    # Parts: from Actual Materials child table only
    for row in (ro.get("actual_materials") or []):
        si.append("items", {
            "item_code": row.item_code,
            "qty": flt(row.qty) or 1,
            "uom": row.uom or "Nos",
            "description": f"{row.description or ''} (RO: {ro.name})".strip()
        })

    # Labor: minutes → hours
    total_minutes = _get_total_minutes_from_tasks_or_aggregate(ro)
    hours = round(total_minutes / 60.0, 2)
    if hours > 0:
        si.append("items", {
            "item_code": ro.labor_item,
            "qty": hours,
            "uom": "Hour",
            "rate": flt(ro.labor_rate) if ro.get("labor_rate") else 0.0,
            "description": f"Labor for {ro.name} ({int(total_minutes)} minutes)"
        })

    si.insert(ignore_permissions=True)
    frappe.msgprint(_("Sales Invoice created: {0}").format(frappe.bold(si.name)))
    return si.name


# ---- Internal utilities ----------------------------------------------------

def _get_ro(name: str) -> Document:
    if not name:
        frappe.throw(_("Repair Order name is required."))
    return frappe.get_doc("Repair Order", name)


def _get_se(name: str) -> Document:
    if not name:
        frappe.throw(_("Stock Entry name is required."))
    se = frappe.get_doc("Stock Entry", name)
    if se.docstatus != 1:
        frappe.throw(_("Stock Entry {0} must be submitted.").format(frappe.bold(name)))
    return se


def _get_total_minutes_from_tasks_or_aggregate(ro: Document) -> float:
    if ro.meta.has_field("total_actual_minutes") and ro.get("total_actual_minutes") is not None:
        return float(ro.total_actual_minutes)
    total = 0.0
    for t in (ro.get("repair_tasks") or []):
        total += float(t.get("actual_minutes") or 0)
    return total


def _mirror_se_items_into_actuals(ro_name: str, se_name: str) -> None:
    """Copy submitted Stock Entry items into RO.actual_materials for at-a-glance visibility."""
    ro = frappe.get_doc("Repair Order", ro_name)
    se = frappe.get_doc("Stock Entry", se_name)

    ro.set("actual_materials", [])
    for it in se.get("items", []):
        ro.append("actual_materials", {
            "item_code": it.item_code,
            "description": it.description,
            "qty": it.qty,
            "uom": it.uom,
            "valuation_rate": it.valuation_rate or 0,
            "amount": flt(it.valuation_rate) * flt(it.qty),
            "stock_entry": se.name
        })
    ro.save(ignore_permissions=True)


# ---- Optional: hook target to auto-mirror on submit ------------------------

def _on_submit_stock_entry(doc: Document, method: str | None = None) -> None:
    ro_name = _extract_ro_from_se(doc)
    if not ro_name or not frappe.db.exists("Repair Order", ro_name):
        return
    _mirror_se_items_into_actuals(ro_name, doc.name)


def _extract_ro_from_se(se: Document) -> str | None:
    if se.get("remarks"):
        for token in str(se.remarks).replace(",", " ").split():
            if token.startswith("RO-"):
                return token.strip()
    for it in se.get("items", []):
        if it.get("description"):
            for token in str(it.description).replace(",", " ").split():
                if token.startswith("RO-"):
                    return token.strip()
    return None


def _truthy(val) -> bool:
    if isinstance(val, bool):
        return val
    try:
        return int(val) != 0
    except Exception:
        return bool(val)
