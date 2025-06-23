# File: repair_portal/service_planning/doctype/component_odometer/component_odometer.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: Track usage of wearable parts and compute % lifespan used

from frappe.model.document import Document


class ComponentOdometer(Document):
    def validate(self):
        if self.usage_cycles and self.expected_lifespan:
            self.lifespan_percent = min(round((self.usage_cycles / self.expected_lifespan) * 100, 2), 100)