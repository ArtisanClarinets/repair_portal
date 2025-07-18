import frappe
from frappe.tests.utils import FrappeTestCase


class TestPortalPermissions(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")

        for email in ("alice@example.com", "bob@example.com", "tech@example.com"):
            if not frappe.db.exists("User", email):
                user = frappe.get_doc({
                    "doctype": "User",
                    "email": email,
                    "first_name": email.split("@")[0],
                })
                user.insert(ignore_permissions=True)

        frappe.get_doc({
            "doctype": "Client Profile",
            "client_name": "Alice",
            "linked_user": "alice@example.com",
        }).insert(ignore_permissions=True)

        frappe.get_doc({
            "doctype": "Client Profile",
            "client_name": "Bob",
            "linked_user": "bob@example.com",
        }).insert(ignore_permissions=True)

        player_a = frappe.get_doc({
            "doctype": "Player Profile",
            "player_name": "A",
            "client_profile": frappe.db.get_value(
                "Client Profile", {"linked_user": "alice@example.com"}
            ),
        }).insert(ignore_permissions=True)

        player_b = frappe.get_doc({
            "doctype": "Player Profile",
            "player_name": "B",
            "client_profile": frappe.db.get_value(
                "Client Profile", {"linked_user": "bob@example.com"}
            ),
        }).insert(ignore_permissions=True)

        frappe.get_doc({
            "doctype": "Instrument Profile",
            "serial_no": "A1",
            "player_profile": player_a.name,
        }).insert(ignore_permissions=True)

        frappe.get_doc({
            "doctype": "Instrument Profile",
            "serial_no": "B1",
            "player_profile": player_b.name,
        }).insert(ignore_permissions=True)

        tech = frappe.get_doc("User", "tech@example.com")
        tech.add_roles("Technician")
        frappe.db.commit()

    def test_customer_cannot_fetch_others(self):
        frappe.set_user("alice@example.com")
        other_client = frappe.db.get_value(
            "Client Profile", {"linked_user": "bob@example.com"}
        )
        with self.assertRaises(frappe.PermissionError):  # noqa: PT027
            frappe.get_doc("Client Profile", other_client)

    def test_technician_can_access(self):
        frappe.set_user("tech@example.com")
        instrument = frappe.db.get_value("Instrument Profile", {"serial_no": "B1"})
        try:
            frappe.get_doc("Instrument Profile", instrument)
        except frappe.PermissionError:
            self.fail("Technician should access instrument")
