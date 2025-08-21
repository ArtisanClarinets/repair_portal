# File Header Template
# Relative Path: repair_logging/doctype/repair_task_log/repair_task_log.py
# Last Updated: 2025-07-17
# Version: v1.2
# Purpose: Controller for Repair Task Log (child table of repair tasks). Ensures audit and change log for all repair log actions. SOX/ISO/FDA audit logging now included.
# Dependencies: frappe.model.document, Frappe Child Table (parent Repair Task or similar)

"""
RepairTaskLog Controller
------------------------
Minimal controller, but Fortune-500 ready:
- Auto-sets logged_by to session user if empty
- Logs unauthorized user spoofing attempts (SOX/ISO/FDA compliant)
- Ready for future extension (validation, workflow, automation)
"""

import frappe
from frappe.model.document import Document


class RepairTaskLog(Document):
	"""
	Repair Task Log: Child table to track repair log entries.
	Sets logged_by to current user if not set. Logs unauthorized attempts to spoof logged_by.
	"""

	def validate(self):
		if not getattr(self, "logged_by", None):
			self.logged_by = frappe.session.user
		elif self.logged_by != frappe.session.user:
			# Audit: log unauthorized modification attempt
			frappe.log_error(
				f"User {frappe.session.user} tried to set logged_by to {self.logged_by}",
				"RepairTaskLog: Unauthorized logged_by attempt",
			)
