# repair_portal/instrument_profile/doctype/document_history/document_history.py
# Updated: 2025-07-01
# Version: 1.0
# Purpose: Controller for Document History child table on Instrument Profile for traceability of service/setup/inspection/ownership events.
# Notes: Used for compliance, full lifecycle trace, and reporting. No custom logic needed; events are linked externally and via the parent Instrument Profile.

import frappe
from frappe.model.document import Document

class DocumentHistory(Document):
    pass
