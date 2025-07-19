# File Header Template
# Relative Path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
# Last Updated: 2025-07-18
# Version: v2.0
# Purpose: Single-source controller for all Clarinet Intake logic, including event blocking, inventory/repair/maintenance rules, and audit logging.
# Dependencies: frappe, Initial Intake Inspection, Clarinet Initial Setup, Serial No

from __future__ import annotations
import logging
import frappe
from frappe.model.document import Document
from frappe import _

LOG = frappe.logger('repair_portal.intake', allow_site=True)
LOG.setLevel(logging.INFO)


def _err(msg: str, title: str) -> None:
    """Log + create an Error Log entry that is visible in the Desk."""
    LOG.error(msg)
    frappe.log_error(msg, title)


class ClarinetIntake(Document):
    """
    All-in-one controller for Clarinet Intake. Handles all business rules, including blocking edits for flagged intakes, inventory/repair/maintenance logic,
    and robust audit logging. Fortune-500 style compliance.
    """

    # Define all required attributes with default values
    workflow_state: str = ''
    intake_type: str = ''
    item_code: str = ''
    serial_no: str = ''
    brand: str = ''
    model: str = ''
    instrument_type: str = ''
    instrument: str = ''
    customer: str = ''
    date_purchased: str = ''
    customer_concerns: str = ''
    instrument_profile: str = ''
    loaner_agreement: str = ''
    warehouse: str = ''

    def before_save(self) -> None:
        """
        Runs before saving any Clarinet Intake. Delegates to intake-type handlers.
        """
        if self.workflow_state == 'Flagged':
            _err(f'Edit blocked on flagged intake {self.name}', 'Flagged Intake Edit')
            frappe.throw(_('Editing is not allowed while intake is Flagged.'))

        if self.intake_type == 'Inventory':
            self._fetch_instrument_details()
            self._handle_inventory_before_save()
            self._handle_instrument_setup_before_save()
        elif self.intake_type == 'Repair':
            self._handle_repair_before_save()
        elif self.intake_type == 'Maintenance':
            self._handle_maintenance_before_save()
        else:
            frappe.throw(_('Intake type must be Inventory, Maintenance, or Repair.'))

    def _fetch_instrument_details(self) -> None:
        """
        Auto-fetch instrument details when instrument is selected for Inventory intake type.
        """
        if self.intake_type == 'Inventory' and self.instrument:
            try:
                instrument_doc = frappe.get_doc('Instrument', self.instrument)
                self.instrument_type = getattr(instrument_doc, 'instrument_type', '')
                self.brand = getattr(instrument_doc, 'brand', '')
                self.model = getattr(instrument_doc, 'model', '')
                self.serial_no = getattr(instrument_doc, 'serial_no', '')
                LOG.info(f'Auto-fetched instrument details for {self.instrument}')
            except frappe.DoesNotExistError:
                frappe.throw(_('Selected Instrument {0} does not exist').format(self.instrument))

    def before_cancel(self) -> None:
        """
        Block cancel if intake is flagged.
        """
        if self.workflow_state == 'Flagged':
            _err(f'Cancel blocked on flagged intake {self.name}', 'Flagged Intake Cancel')
            frappe.throw(_('Canceling a flagged intake is prohibited.'))

    def on_trash(self) -> None:
        """
        Block delete if intake is flagged. Give user feedback on linked docs.
        Optionally mark checklist items completed.
        """
        if self.workflow_state == 'Flagged':
            _err(f'Delete blocked on flagged intake {self.name}', 'Flagged Intake Delete')
            frappe.throw(_('Deleting a flagged intake is not allowed.'))
        if getattr(self, 'instrument_profile', None):
            frappe.msgprint(
                _('Instrument Profile {0} linked to this Intake will remain intact.').format(
                    self.instrument_profile
                )
            )
        if getattr(self, 'loaner_agreement', None):
            frappe.msgprint(
                _('Loaner Agreement {0} linked to this Intake will remain intact.').format(
                    self.loaner_agreement
                )
            )
        if frappe.db.exists('Intake Checklist Item', {'parent': self.name}):
            frappe.db.set_value(
                'Intake Checklist Item',
                {'parent': self.name},
                {'status': 'Completed'},
            )

    def _handle_instrument_setup_before_save(self) -> None:
        """
        Auto-create related docs for new inventory: Instrument, Instrument Profile, Instrument Inspection, Clarinet Initial Setup.
        """
        if self.intake_type == 'Inventory':
            frappe.get_doc(
                {
                    'doctype': 'Instrument',
                    'serial_no': self.serial_no,
                    'item_code': self.item_code,
                    'brand': self.brand,
                    'model': self.model,
                }
            ).insert(ignore_permissions=True)
            frappe.get_doc(
                {
                    'doctype': 'Instrument Profile',
                    'instrument': self.serial_no,
                    'instrument_profile': self.instrument_profile,
                }
            ).insert(ignore_permissions=True)
            frappe.get_doc(
                {
                    'doctype': 'Instrument Inspection',
                    'instrument': self.serial_no,
                }
            ).insert(ignore_permissions=True)
            frappe.get_doc(
                {
                    'doctype': 'Clarinet Initial Setup',
                    'clarinet_intake': self.name,
                    'item_code': self.item_code,
                }
            ).insert(ignore_permissions=True)

    def _handle_inventory_before_save(self) -> None:
        """
        Business rules for inventory intakes: create Serial No, required item_code, and dependency docs.
        """
        try:
            if not getattr(self, 'item_code', None):
                frappe.throw(_('Item Code is mandatory for inventory intakes.'))
            self._create_serial_no()
            self._create_inventory_dependencies()
        except Exception:
            frappe.log_error(
                frappe.get_traceback(), _(f'Inventory intake before_save failed for {self.name}')
            )
            raise

    def _handle_repair_before_save(self) -> None:
        """
        Placeholder for repair-specific logic.
        """
        pass  # Extend with repair auto-tasks

    def _handle_maintenance_before_save(self) -> None:
        """
        Placeholder for maintenance-specific logic.
        """
        pass  # Extend with maintenance auto-tasks

    def _create_serial_no(self) -> None:
        """
        Creates a Serial No record if not already set.
        """
        if not getattr(self, 'serial_no', None):
            sn_doc = frappe.get_doc(
                {
                    'doctype': 'Serial No',
                    'item_code': self.item_code,
                    'serial_no': frappe.get_value('Serial Number', {'serial_no': self.serial_no}),
                    'warehouse': getattr(self, 'warehouse', None),
                    'status': 'Active',
                    'purchase_document_type': 'Clarinet Intake',
                    'purchase_document_no': self.name,
                }
            )
            sn_doc.insert(ignore_permissions=True)
            serial_value = (
                frappe.get_value('Serial Number', {'serial_no': self.serial_no})
                if self.serial_no
                else ''
            )
            self.serial_no = str(serial_value) if serial_value is not None else ''

    def _create_inventory_dependencies(self) -> None:
        """
        Auto-create related docs for new inventory: Initial Intake Inspection, Clarinet Initial Setup.
        """
        frappe.get_doc(
            {
                'doctype': 'Initial Intake Inspection',
                'clarinet_intake': self.name,
                'item_code': self.item_code,
                'serial_no': self.serial_no,
            }
        ).insert(ignore_permissions=True)
        frappe.get_doc(
            {
                'doctype': 'Clarinet Initial Setup',
                'clarinet_intake': self.name,
                'item_code': self.item_code,
                'serial_no': self.serial_no,
            }
        ).insert(ignore_permissions=True)
