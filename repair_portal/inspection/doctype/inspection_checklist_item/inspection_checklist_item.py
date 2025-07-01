# File: repair_portal/inspection/doctype/inspection_checklist_item/inspection_checklist_item.py
# Updated: 2025-06-27
# Version: 1.0
# Purpose: Child table for storing each individual inspection step, auto-populated from selected procedure or JSON
# Notes: Designed for modular QA/Repair/Setup flows for all instrument types. Used in Inspection Report table.

from frappe.model.document import Document


class InspectionChecklistItem(Document):
    pass
