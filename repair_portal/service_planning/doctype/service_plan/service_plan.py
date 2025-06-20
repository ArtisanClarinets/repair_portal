# File: repair_portal/service_planning/doctype/service_plan/service_plan.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: Logic for predictive maintenance planning and reminders

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_days

class ServicePlan(Document):
    def before_save(self):
        if self.play_hours and self.play_hours > 0:
            interval = 250  # Placeholder threshold for prediction
            days_ahead = int((interval - self.play_hours) * 0.2)
            self.next_service_prediction = add_days(nowdate(), days_ahead)

    def on_submit(self):
        if self.reminder_enabled:
            frappe.msgprint("Calendar reminder setup will be initiated.")