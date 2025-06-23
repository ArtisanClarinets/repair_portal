import unittest

import frappe

from repair_portal.instrument_profile.utils import get_instrument_timeline


class TestInstrumentTimeline(unittest.TestCase):
    def test_timeline_generation(self):
        frappe.set_user("Administrator")
        inst = frappe.get_doc(
            {
                "doctype": "Instrument Profile",
                "instrument_category": "Clarinet",
                "serial_number": "TLN-001",
                "route": "tln-001",
            }
        ).insert()
        inst.append(
            "instrument_events",
            {
                "date": "2025-07-10",
                "event_type": "Service",
                "description": "Initial setup",
            },
        )
        inst.save()

        frappe.get_doc(
            {
                "doctype": "Instrument Comment",
                "instrument_profile": inst.name,
                "comment": "Great sound!",
            }
        ).insert()

        events = get_instrument_timeline(inst.name)
        assert len(events) >= 2
