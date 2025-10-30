# Path: repair_portal/repair_portal/doctype/shipment_photo/shipment_photo.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Shipment Photo child table - handles shipping documentation photos.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class ShipmentPhoto(Document):
    """Child table controller for Shipment Photo records."""

    def validate(self):
        """Validate photo requirements."""
        if not self.image:
            frappe.throw(_("Image is required"))