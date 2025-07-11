
#!/usr/bin/env python3
"""
Create & publish Website Items for all Items
flagged show_in_clarinetfest_2025 = 1 (Frappe v15).
Usage:
  bench --site erp.artisanclarinets.com execute repair_portal.scripts.make_clarinetfest_ws_items.run
"""
import frappe

def run():
    item_codes = frappe.get_all(
        "Item",
        filters={"disabled": 0, "show_in_clarinetfest_2025": 1},
        pluck="name",
    )

    created = 0
    for code in item_codes:
        if frappe.db.exists("Website Item", {"item_code": code}):
            continue

        doc = frappe.get_doc({
            "doctype": "Website Item",
            "item_code": code,
            "published": 1,
            "web_item_name": frappe.db.get_value("Item", code, "item_name"),
            "website_image": frappe.db.get_value("Item", code, "image"),
            "website_description": frappe.db.get_value("Item", code, "description"),
        })
        doc.insert(ignore_permissions=True)
        created += 1

    frappe.db.commit()
    print(f"✓ Created {created} Website Item(s)")
