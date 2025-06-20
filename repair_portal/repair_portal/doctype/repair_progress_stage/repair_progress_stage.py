# File: repair_portal/repair_portal/doctype/repair_progress_stage/repair_progress_stage.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: Tracks progress stages for repairs to render progress thermometer in the portal.

import frappe
from frappe.model.document import Document

class RepairProgressStage(Document):
    def validate(self):
        if self.completed and not self.timestamp:
            self.timestamp = frappe.utils.now_datetime()