# Relative Path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
# Version: v3.0
# Author: Production-grade implementation for high-volume environments
# Purpose: End-to-end Clarinet Intake lifecycle handling
# Dependencies: Frappe Framework >= v15

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
import frappe.utils

from . import clarinet_intake_block_flagged

class ClarinetIntake(Document):
    """
    Clarinet Intake Controller
    Handles validation, lifecycle hooks, and automatic related record creation.
    """

    # Define all expected attributes with default values (for type checking and IDEs)
    intake_type: str = ""
    qc_status: str = ""
    workflow_state: str = ""
    serial_number: str = ""
    item_code: str = ""
    item_name: str = ""
    supplier: str = ""
    warehouse: str = ""
    purchase_receipt: str = ""
    instrument_profile: str = ""
    stock_status: str = ""
    customer: str = ""
    due_date: str = ""
    # 'name' is inherited from Document; do not override its type here

    def validate(self) -> None:
        """Core validations before saving."""
        self._validate_workflow_state()
        self._validate_required_fields()
        self._validate_unique_serial()
        self._ensure_item()
        self._ensure_purchase_receipt()
        self._ensure_serial_no()
        self._ensure_instrument_profile()
        self._ensure_quality_inspection()
        self._sync_instrument_profile()

    def before_insert(self) -> None:
        """Ensure proper permissions and initialization."""
        self._check_write_permissions()

    def before_save(self) -> None:
        """Run flag check prior to save."""
        clarinet_intake_block_flagged.before_save(self)

    def before_submit(self) -> None:
        """Verify that QC is passed before submit."""
        if self.intake_type == "Inventory" and self.qc_status == "Fail":
            frappe.throw(_("QC Failed — resolve QC issues before submitting this Intake."))
        self._check_submit_permissions()

    def before_cancel(self) -> None:
        """Block cancel if flagged."""
        clarinet_intake_block_flagged.before_cancel(self)
        self._check_cancel_permissions()

    def on_submit(self) -> None:
        """Log submission and ensure related data consistency."""
        self._log_transition("Submitted")

    def on_update(self) -> None:
        """Update Instrument Profile status when intake is edited."""
        if self.has_value_changed("stock_status"):
            self._update_profile_stock_status()
        if self.has_value_changed("qc_status"):
            self._apply_qc_hold()
            self._release_qc_hold_if_passed()

    # ---------------------------
    # Validation Helpers
    # ---------------------------
    def _validate_workflow_state(self) -> None:
        valid_states = {"Pending", "QC", "Flagged", "Completed"}
        if self.workflow_state and self.workflow_state not in valid_states:
            frappe.throw(_("Invalid workflow state: {0}").format(self.workflow_state))

    def _validate_required_fields(self) -> None:
        """Ensure required fields are present depending on intake type."""
        if self.intake_type == "Inventory":
            required = ["purchase_order", "warehouse"]
        else:
            required = ["customer", "due_date"]

        for field in required:
            if not self.get(field):
                frappe.throw(
                    _("{0} is required for {1} Intake.").format(
                        frappe.bold(field.replace("_", " ").title()),
                        self.intake_type
                    )
                )

    def _validate_unique_serial(self) -> None:
        """Ensure no duplicate serial numbers across intakes."""
        if self.serial_number and frappe.db.exists(
            "Clarinet Intake",
            {
                "serial_number": self.serial_number,
                "name": ["!=", self.name]
            }
        ):
            frappe.throw(_("This Serial Number is already registered in another Intake."))

    # ---------------------------
    # Creation Helpers
    # ---------------------------
    def _ensure_item(self) -> None:
        """Create Item if it does not exist."""
        if not self.item_code:
            frappe.throw(_("Item Code is required."))
        if frappe.db.exists("Item", self.item_code):
            return
        item = frappe.new_doc("Item")
        item.update({
            "item_code": self.item_code,
            "item_name": self.item_name or self.item_code,
            "item_group": "Clarinets",
            "is_stock_item": 1,
            "has_serial_no": 1,
            "stock_uom": "Nos"
        })
        item.insert()

    def _ensure_purchase_receipt(self) -> None:
        """Auto-link or create Purchase Receipt for Inventory."""
        if self.intake_type != "Inventory":
            return

        if self.purchase_receipt:
            return

        existing_pr = frappe.db.get_value(
            "Purchase Receipt Item",
            {
                "item_code": self.item_code,
                "serial_no": self.serial_number
            },
            "parent"
        )
        if existing_pr:
            if isinstance(existing_pr, str):
                self.purchase_receipt = existing_pr
            elif existing_pr is not None:
                self.purchase_receipt = str(existing_pr)
            return

        pr = frappe.new_doc("Purchase Receipt")
        pr.update({"supplier": self.supplier or "Unknown"})
        pr.append("items", {
            "item_code": self.item_code,
            "qty": 1,
            "warehouse": self.warehouse,
            "serial_no": self.serial_number
        })
        pr.insert()
        if pr.name is not None:
            self.purchase_receipt = str(pr.name)
        else:
            frappe.throw(_("Failed to create Purchase Receipt: No name returned."))

    def _ensure_serial_no(self) -> None:
        """Ensure Serial No is created and linked."""
        if self.intake_type != "Inventory":
            return
        if not self.serial_number:
            frappe.throw(_("Serial Number is required."))
        if frappe.db.exists("Serial No", self.serial_number):
            return

        sn = frappe.new_doc("Serial No")
        sn.update({
            "serial_no": self.serial_number,
            "item_code": self.item_code,
            "warehouse": self.warehouse,
            "status": "Active",
            "purchase_document_type": "Purchase Receipt",
            "purchase_document_no": self.purchase_receipt
        })
        sn.insert()

    def _ensure_instrument_profile(self) -> None:
        """Create or attach Instrument Profile."""
        if self.instrument_profile:
            return
        ip = frappe.db.get_value(
            "Instrument Profile",
            {"serial_number": self.serial_number},
            "name"
        )
        if ip:
            self.instrument_profile = str(ip)
            return

        ip_doc = frappe.new_doc("Instrument Profile")
        ip_doc.update({
            "serial_number": self.serial_number,
            "model": self.item_name,
            "item_code": self.item_code,
            "status": self.stock_status or "New Intake",
            "latest_intake": self.name
        })
        ip_doc.insert()
        self.instrument_profile = str(ip_doc.name or "")

    def _ensure_quality_inspection(self) -> None:
        """Auto-create incoming QC record."""
        if self.intake_type != "Inventory":
            return
        if frappe.db.exists(
            "Quality Inspection",
            {
                "reference_type": "Purchase Receipt",
                "reference_name": self.purchase_receipt,
                "item_code": self.item_code,
                "inspection_type": "Incoming"
            }
        ):
            return

        qi = frappe.new_doc("Quality Inspection")
        qi.update({
            "inspection_type": "Incoming",
            "reference_type": "Purchase Receipt",
            "reference_name": self.purchase_receipt,
            "item_code": self.item_code,
            "sample_size": 1,
            "report_date": frappe.utils.nowdate()
        })
        qi.insert()

    # ---------------------------
    # Profile Updates
    # ---------------------------
    def _sync_instrument_profile(self) -> None:
        """Update Instrument Profile status and reference."""
        if not self.instrument_profile:
            return
        ip = frappe.get_doc("Instrument Profile", self.instrument_profile)
        ip.db_set("status", self.stock_status or "Under Review")
        ip.db_set("latest_intake", self.name)

    def _update_profile_stock_status(self) -> None:
        if not self.instrument_profile:
            return
        ip = frappe.get_doc("Instrument Profile", self.instrument_profile)
        ip.db_set("status", self.stock_status)

    def _apply_qc_hold(self) -> None:
        if self.intake_type == "Inventory" and self.qc_status == "Fail":
            self.db_set("stock_status", "Hold")

    def _release_qc_hold_if_passed(self) -> None:
        if (
            self.intake_type == "Inventory" and
            self.qc_status == "Pass" and
            self.stock_status == "Hold"
        ):
            self.db_set("stock_status", "Available")

    # ---------------------------
    # Permissions & Logging
    # ---------------------------
    def _check_submit_permissions(self) -> None:
        if not frappe.has_permission(self.doctype, "submit"):
            frappe.throw(_("You do not have permission to submit this Intake."))

    def _check_write_permissions(self) -> None:
        if not frappe.has_permission(self.doctype, "write"):
            frappe.throw(_("You do not have permission to save this Intake."))

    def _check_cancel_permissions(self) -> None:
        if not frappe.has_permission(self.doctype, "cancel"):
            frappe.throw(_("You do not have permission to cancel this Intake."))

    def _log_transition(self, action: str) -> None:
        self.add_comment(
            "Comment",
            _("Workflow action '{0}' performed by {1}").format(
                action, frappe.session.user
            )
        )
