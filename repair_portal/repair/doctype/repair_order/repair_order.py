# Relative Path: repair_portal/repair/doctype/repair_order/repair_order.py
# Version: 2.3.0 (2025-09-17)
# Purpose:
#   Hardened server logic for Repair Order with:
#     - Defaults from Single "Repair Settings"
#     - Workflow state validation (advisory, schema-safe)
#     - Optional normalization into 'related_documents' child table
#     - Materials actuals mirrored from Stock Entry
#     - Sales Invoice generation (parts + labor minutes→hours)
#     - Warranty flags synced from Instrument Profile (if available)
#     - (New) Stock Entry draft prefilled from Planned Materials (optional)
#
# Safe on sites where some optional fields/child tables are absent.

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate

CANONICAL_WORKFLOW_STATES = [
    "Draft",
    "In Progress",
    "QA",
    "Ready",
    "Delivered",
    "Closed",
]


class RepairOrder(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from repair_portal.repair.doctype.repair_actual_material.repair_actual_material import (
            RepairActualMaterial,
        )
        from repair_portal.repair.doctype.repair_planned_material.repair_planned_material import (
            RepairPlannedMaterial,
        )
        from repair_portal.repair.doctype.repair_related_document.repair_related_document import (
            RepairRelatedDocument,
        )

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
            rs = frappe.get_single("Repair Settings")
        except Exception:
            rs = None
        if not rs:
            return

        if not self.get("company") and rs.get("default_company"):
            self.company = rs.default_company
        if not self.get("warehouse_source") and rs.get("default_source_warehouse"):
            self.warehouse_source = rs.default_source_warehouse
        if not self.get("labor_item") and rs.get("default_labor_item"):
            self.labor_item = rs.default_labor_item
        if not self.get("labor_rate") and rs.get("default_labor_rate"):
            self.labor_rate = rs.default_labor_rate

        if self.meta.has_field("qa_required") and self.qa_required is None:
            self.qa_required = 1 if flt(rs.get("default_qa_required")) else 0
        if self.meta.has_field("require_invoice_before_delivery") and self.require_invoice_before_delivery is None:
            self.require_invoice_before_delivery = 1 if flt(rs.get("default_require_invoice_before_delivery")) else 0

    # ---- Validations -------------------------------------------------------

    def _validate_workflow_state(self) -> None:
        """Advisory validation on workflow_state; skip cleanly if field absent."""
        if not self.meta.has_field("workflow_state"):
            return

        ws = self.get("workflow_state")
        if not ws:
            frappe.msgprint(
                _("Repair Order is missing a workflow state; defaulting to Draft."),
                alert=True, indicator="orange",
            )
            self.workflow_state = "Draft"
            ws = "Draft"

        if ws not in CANONICAL_WORKFLOW_STATES:
            frappe.msgprint(
                _("Workflow state '{0}' is not in the recommended set: {1}")
                .format(frappe.bold(ws), ", ".join(CANONICAL_WORKFLOW_STATES)),
                alert=True, indicator="orange",
            )

        # Early operator guidance (no throw)
        required_now = []
        if not self.get("customer"):
            required_now.append("Customer")
        if not self.get("warehouse_source"):
            required_now.append("Source Warehouse")
        if not self.get("labor_item"):
            required_now.append("Labor Item (Service)")
        if required_now:
            frappe.msgprint(
                _("Missing recommended fields on Repair Order: {0}")
                .format(", ".join(required_now)),
                alert=True, indicator="orange",
            )

    # ---- Related Documents -------------------------------------------------

    def _normalize_links(self) -> None:
        """If 'related_documents' exists, add first-class links for operator context."""
        if not self.meta.has_field("related_documents"):
            return

        def opt(fieldname: str) -> str | None:
            return self.get(fieldname) if self.meta.has_field(fieldname) else None

        link_candidates = {
            # Optional stage links only if such fields exist on schema
            "Clarinet Intake": ["clarinet_intake", "intake"],
            "Instrument Inspection": ["instrument_inspection"],
            "Service Plan": ["service_plan"],
            "Repair Estimate": ["repair_estimate"],
            "Measurement Session": ["measurement_session"],
            # Always attempt to include Instrument Profile (first-class)
            "Instrument Profile": ["instrument_profile"],
        }
        for dt, candidates in link_candidates.items():
            for fieldname in candidates:
                name = opt(fieldname)
                if name:
                    self._ensure_related(dt, name, desc="Stage link")
                    break

    def _ensure_related(self, doctype: str, name: str, desc: str = "") -> None:
        rows = (self.related_documents or []) if self.meta.has_field("related_documents") else []
        exists = any((row.doctype_name == doctype and row.document_name == name) for row in rows)
        if not exists and self.meta.has_field("related_documents"):
            self.append("related_documents", {
                "doctype_name": doctype,
                "document_name": name,
                "description": desc
            })

    def _dedupe_related(self) -> None:
        if not self.meta.has_field("related_documents"):
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
        if not self.get("instrument_profile"):
            if self.meta.has_field("is_warranty"):
                self.is_warranty = 0
            return

        warranty_date = None
        try:
            ip = frappe.get_doc("Instrument Profile", self.instrument_profile)
            for candidate in ("warranty_until", "warranty_end_date"):
                if hasattr(ip, candidate) and ip.get(candidate):
                    warranty_date = getdate(ip.get(candidate))
                    break
        except Exception:
            warranty_date = None

        if self.meta.has_field("warranty_until"):
            self.warranty_until = warranty_date if warranty_date else None

        if self.meta.has_field("is_warranty"):
            if warranty_date and getdate(nowdate()) <= warranty_date:
                self.is_warranty = 1
            else:
                self.is_warranty = 0

    # ---- Utility for client 'Create' shortcuts -----------------------------

    @frappe.whitelist()
    def create_child(self, doctype: str) -> dict:
        if not doctype:
            frappe.throw(_("doctype is required"))
        opts = {
            "repair_order": self.name,
            "customer": self.get("customer"),
            "instrument_profile": self.get("instrument_profile"),
        }
        return {"doctype": doctype, "route_options": opts}


# ===========================================================================
# ERPNext Integrations (Actuals via Stock Entry, Invoice generation)
# ===========================================================================

@frappe.whitelist()
def create_material_issue_draft(repair_order: str, include_planned: int | bool = 0) -> list[str]:
    """Create a draft Stock Entry (Material Issue).
    Args:
        repair_order: Repair Order name
        include_planned: if truthy, prefill items from planned_materials
    Returns:
        [Stock Entry name]
    """
    ro = _get_ro(repair_order)
    company = ro.get("company") or frappe.defaults.get_global_default("company")
    if not company:
        frappe.throw(_("Company is required (set on Repair Order or defaults)."))
    if not ro.get("warehouse_source"):
        frappe.throw(_("Source Warehouse is required on the Repair Order."))

    se = frappe.new_doc("Stock Entry")
    se.purpose = "Material Issue"
    se.company = company
    se.set_posting_time = 1
    se.remarks = f"Materials for {ro.name}"

    if _truthy(include_planned) and ro.meta.has_field("planned_materials"):
        for pm in (ro.get("planned_materials") or []):
            if not pm.get("item_code") or not flt(pm.get("qty")):
                continue
            se.append("items", {
                "item_code": pm.item_code,
                "qty": flt(pm.qty),
                "uom": pm.uom or "Nos",
                "s_warehouse": ro.warehouse_source,
                "description": (pm.description or f"Planned for {ro.name}")
            })

    se.insert(ignore_permissions=True)
    return [se.name]


@frappe.whitelist()
def refresh_actuals_from_stock_entry(repair_order: str, stock_entry: str) -> None:
    ro = _get_ro(repair_order)
    _mirror_se_items_into_actuals(ro.name, _get_se(stock_entry).name)


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
