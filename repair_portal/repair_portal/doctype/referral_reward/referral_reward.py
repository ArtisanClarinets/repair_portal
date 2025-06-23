# File: repair_portal/repair_portal/doctype/referral_reward/referral_reward.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: Tracks referral relationships and reward statuses in the client portal.

import frappe
from frappe.model.document import Document


class ReferralReward(Document):
    def validate(self):
        if self.status == "Rewarded" and not self.date_awarded:
            self.date_awarded = frappe.utils.nowdate()