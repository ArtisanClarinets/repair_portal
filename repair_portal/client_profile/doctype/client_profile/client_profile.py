# Relative Path: repair_portal/client_profile/doctype/client_profile/client_profile.py
# Last Updated: 2025-07-16
# Version: v2.0
# Purpose: Refactored controller for Client Profile extension of ERPNext Customer
# Dependencies: Customer, Player Profile, Instrument Profile, Repair Log, Clarinet Inspection

import frappe
from frappe.model.document import Document


class ClientProfile(Document):
    def on_update(self):
        """Pulls linked child data based on Customer ID."""
        try:
            if not self.customer:
                return

            mappings = [
                ("owned_instruments", "Instrument Profile", {"customer": self.customer}, ["name", "serial_no", "model"], ["instrument", "serial_no", "model"]),
                ("linked_players", "Player Profile", {"customer": self.customer}, ["name", "player_name"], ["player", "player_name"]),
                ("repair_logs", "Repair Log", {"customer": self.customer}, ["name", "date", "summary"], ["repair_log", "date", "summary"]),
                ("leak_tests", "Leak Test", {"customer": self.customer}, ["name", "test_date"], ["test", "test_date"]),
                ("tone_sessions", "Intonation Session", {"customer": self.customer}, ["name", "session_date"], ["session", "session_date"]),
                ("qa_findings", "Clarinet Inspection", {"customer": self.customer}, ["name", "status"], ["inspection", "status"]),
                ("setup_logs", "Clarinet Setup Log", {"customer": self.customer}, ["name", "setup_date"], ["setup_log", "setup_date"])
            ]

            for table_field, doctype, filters, src_fields, tgt_fields in mappings:
                self.set(table_field, [])
                rows = frappe.get_all(doctype, filters=filters, fields=src_fields)
                for r in rows:
                    self.append(table_field, dict(zip(tgt_fields, [r[f] for f in src_fields])))
        except Exception:
            frappe.log_error(frappe.get_traceback(), "ClientProfile: on_update sync failed")