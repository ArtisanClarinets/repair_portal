import frappe, json

def execute():
    if frappe.db.exists("Workspace", "repair-portal"):
        frappe.delete_doc("Workspace", "repair-portal", force=True)

    content_blocks = [
        {"type": "link", "label": "Intake", "link_type": "Workspace", "link_to": "intake-workspace", "col": 6},
        {"type": "link", "label": "Inspection", "link_type": "Workspace", "link_to": "inspection-workspace", "col": 6},
        {"type": "link", "label": "Service Planning", "link_type": "Workspace", "link_to": "service-planning-workspace", "col": 6},
        {"type": "link", "label": "Repair Logging", "link_type": "Workspace", "link_to": "repair-logging-workspace", "col": 6},
        {"type": "link", "label": "Final QA", "link_type": "Workspace", "link_to": "qa-workspace", "col": 6},
        {"type": "link", "label": "Repair Tools", "link_type": "Workspace", "link_to": "repair-tools-workspace", "col": 6},
        {"type": "link", "label": "Repair Enhancements", "link_type": "Workspace", "link_to": "repair-enhancements-workspace", "col": 6}
    ]

    doc = frappe.get_doc({
        "doctype": "Workspace",
        "name": "repair-portal",
        "label": "Repair Portal",
        "title": "Repair Portal",
        "module": "Repair Portal",
        "public": 1,
        "is_standard": 1,
        "content": json.dumps(content_blocks)
    })

    doc.insert(ignore_permissions=True)
    frappe.db.commit()