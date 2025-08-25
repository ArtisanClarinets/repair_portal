 # Copyright (c) 2025
# Repair Order: central hub linking all repair workflow artifacts.

from __future__ import annotations
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint


ALLOWED_STATUS = [
    "Draft",
    "Intake",
    "Diagnostics",
    "Structural",
    "Pads & Sealing",
    "Setup",
    "QA",
    "Ready for Pickup",
    "Delivered",
    "Cancelled",
]
class RepairOrder(Document):
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF


    # end: auto-generated types

    def validate(self):
        self._validate_status()
        self._dedupe_related()
        self._normalize_links()
        # Optional: prevent Delivery when open tasks exist (extend later)

    def _validate_status(self):
        if self.status not in ALLOWED_STATUS: # type: ignore
            frappe.throw(_("Invalid status: {0}").format(frappe.bold(self.status))) # type: ignore

    def _normalize_links(self):
        """When a first-class link is present, ensure it appears in Related Documents too."""
        linkmap = {
            "Clarinet Intake": self.clarinet_intake, # type: ignore
            "Instrument Inspection": self.instrument_inspection, # type: ignore
            "Service Plan": self.service_plan, # type: ignore
            "Repair Estimate": self.repair_estimate, # type: ignore
            "Final QA Checklist": self.final_qa_checklist, # type: ignore
            "Measurement Session": self.measurement_session, # type: ignore
        }
        for dt, name in linkmap.items():
            if name:
                self._ensure_related(dt, name, desc="Stage link")

    def _ensure_related(self, doctype: str, name: str, desc: str = ""):
        if not self.related_documents:
            self.related_documents = []
        exists = any(
            (row.doctype_name == doctype and row.document_name == name)
            for row in self.related_documents
        )
        if not exists:
            self.append("related_documents", {
                "doctype_name": doctype,
                "document_name": name,
                "description": desc,
            })

    def _dedupe_related(self):
        seen = set()
        deduped = []
        for row in self.related_documents or []:
            key = (row.doctype_name, row.document_name)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(row)
        self.related_documents = deduped

    @frappe.whitelist()
    def create_child(self, doctype: str) -> dict:
        """
        Helper to start a child doc with route_options pre-filled (client uses frappe.new_doc).
        Returns a dict of route_options for convenience.
        """
        if not doctype:
            frappe.throw(_("doctype is required"))
        opts = {
            "repair_order": self.name,
            "customer": self.customer, # type: ignore
            "instrument_profile": self.instrument_profile, # type: ignore
        }
        return {"doctype": doctype, "route_options": opts}
