# Relative Path: repair_portal/client_profile/doctype/client_profile/client_profile.py
# Last Updated: 2025-07-14
# Version: v1.4
# Purpose: Handles customer sync, rename logic, and populates all child trackers for instruments, players, and logs
# Dependencies: Customer, Contact, Player Profile, Instrument Profile, Repair Log, Clarinet Inspection, etc.

import frappe
from frappe.model.document import Document

class ClientProfile(Document):
    def on_update(self):
        try:
            mappings = [
                ("owned_instruments", "Instrument Profile", {"client_profile": self.name}, ["name", "serial_no", "model"], ["instrument", "serial_no", "model"]),
                ("linked_players", "Player Profile", {"client_profile": self.name}, ["name", "player_name"], ["player", "player_name"]),
                ("repair_logs", "Repair Log", {"client_profile": self.name}, ["name", "date", "summary"], ["repair_log", "date", "summary"]),
                ("leak_tests", "Leak Test", {"client_profile": self.name}, ["name", "test_date"], ["test", "test_date"]),
                ("tone_sessions", "Intonation Session", {"client_profile": self.name}, ["name", "session_date"], ["session", "session_date"]),
                ("qa_findings", "Clarinet Inspection", {"client_profile": self.name}, ["name", "status"], ["inspection", "status"]),
                ("setup_logs", "Clarinet Setup Log", {"client_profile": self.name}, ["name", "setup_date"], ["setup_log", "setup_date"])
            ]

            for table_field, doctype, filters, src_fields, tgt_fields in mappings:
                self.set(table_field, [])
                rows = frappe.get_all(doctype, filters=filters, fields=src_fields)
                for r in rows:
                    self.append(table_field, dict(zip(tgt_fields, [r[f] for f in src_fields])))
        except Exception:
            frappe.log_error(frappe.get_traceback(), "ClientProfile: on_update tracker sync failed")