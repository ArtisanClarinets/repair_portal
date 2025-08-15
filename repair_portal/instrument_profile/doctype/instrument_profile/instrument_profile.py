# Path: repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Last Updated: 2025-08-14
# Version: v2.0
# Purpose: Enforce read-only snapshot semantics on managed fields and trigger sync.
from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe import _

from repair_portal.instrument_profile.services.profile_sync import sync_profile

READ_ONLY_FIELDS = {
    "serial_no",
    "brand",
    "model",
    "instrument_category",
    "customer",
    "owner_name",
    "purchase_date",
    "purchase_order",
    "purchase_receipt",
    "warranty_start_date",
    "warranty_end_date",
    "status",
    "headline",
}


class InstrumentProfile(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from repair_portal.instrument_profile.doctype.external_work_logs.external_work_logs import ExternalWorkLogs
        from repair_portal.instrument_profile.doctype.instrument_accessory.instrument_accessory import InstrumentAccessory
        from repair_portal.instrument_profile.doctype.instrument_condition_record.instrument_condition_record import InstrumentConditionRecord
        from repair_portal.instrument_profile.doctype.instrument_photo.instrument_photo import InstrumentPhoto
        from repair_portal.repair_logging.doctype.instrument_interaction_log.instrument_interaction_log import InstrumentInteractionLog
        from repair_portal.repair_logging.doctype.material_use_log.material_use_log import MaterialUseLog
        from repair_portal.repair_logging.doctype.warranty_modification_log.warranty_modification_log import WarrantyModificationLog

        accessory_log: DF.Table[InstrumentAccessory]
        amended_from: DF.Link | None
        body_material: DF.Data | None
        brand: DF.Data | None
        condition_logs: DF.Table[InstrumentConditionRecord]
        current_location: DF.Data | None
        customer: DF.Link | None
        external_work_logs: DF.Table[ExternalWorkLogs]
        headline: DF.Data | None
        initial_condition_notes: DF.Text | None
        instrument: DF.Link
        instrument_category: DF.Data | None
        instrument_profile_id: DF.Data | None
        intake_date: DF.Date | None
        interaction_logs: DF.Table[InstrumentInteractionLog]
        key_plating: DF.Data | None
        key_system: DF.Literal["Boehm", "Albert", "Oehler", "Other"]
        linked_inspection: DF.Link | None
        material_usage: DF.Table[MaterialUseLog]
        model: DF.Data | None
        number_of_keys_rings: DF.Data | None
        owner_name: DF.Data | None
        profile_image: DF.AttachImage | None
        purchase_date: DF.Date | None
        purchase_order: DF.Link | None
        purchase_receipt: DF.Link | None
        serial_no: DF.Data | None
        serial_photos: DF.Table[InstrumentPhoto]
        service_photos: DF.Table[InstrumentPhoto]
        status: DF.Data | None
        warranty_end_date: DF.Date | None
        warranty_expiration: DF.Date | None
        warranty_logs: DF.Table[WarrantyModificationLog]
        warranty_start_date: DF.Date | None
        wood_type: DF.Data | None
        workflow_state: DF.Literal["Open", "In Progress", "Delivered", "Archived"]
    # end: auto-generated types
    """
    Instrument Profile acts as a "materialized view" of Instrument identity data.
    Managed fields are synced from canonical doctypes and should not be edited manually.
    """

    def validate(self):
        # Skip enforcement during programmatic sync
        if getattr(frappe.flags, "in_profile_sync", False):
            return

        if frappe.session.user != "Administrator" and not frappe.has_role("System Manager"):
            dirty = [f for f in self.get_dirty_fields() if f in READ_ONLY_FIELDS]
            if dirty:
                frappe.throw(
                    _("These fields are managed automatically and cannot be edited: {0}")
                    .format(", ".join(dirty))
                )

    def on_update(self):
        """Refresh derived fields from canonical doctypes on any change."""
        if getattr(frappe.flags, "in_profile_sync", False):
            return
        try:
            frappe.flags.in_profile_sync = True
            sync_profile(self.name)
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"InstrumentProfile: sync failed ({self.name})")
        finally:
            frappe.flags.in_profile_sync = False

    def after_insert(self):
        if getattr(frappe.flags, "in_profile_sync", False):
            return
        try:
            frappe.flags.in_profile_sync = True
            sync_profile(self.name)
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"InstrumentProfile: initial sync failed ({self.name})")
        finally:
            frappe.flags.in_profile_sync = False
