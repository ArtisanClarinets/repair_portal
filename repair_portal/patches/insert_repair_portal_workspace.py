import frappe

def execute():
    if not frappe.db.table_exists("Workspace"):
        frappe.reload_doc("desk", "doctype", "workspace")
        frappe.db.commit()

    if not frappe.db.exists("Workspace", "repair-portal"):
        frappe.get_doc({
            "doctype": "Workspace",
            "name": "repair-portal",
            "label": "Repair Portal",
            "module": "Repair Portal",
            "is_standard": 1,
            "public": 1,
            "content": [
                {"type": "doctype", "data": {"name": "Instrument Intake Form", "label": "Intake", "col": 6}},
                {"type": "doctype", "data": {"name": "Repair Task Log", "label": "Repairs", "col": 6}},
                {"type": "doctype", "data": {"name": "Service Plan", "label": "Service Plans", "col": 6}},
                {"type": "doctype", "data": {"name": "Final QA Checklist", "label": "Final QA", "col": 6}},
                {"type": "doctype", "data": {"name": "Clarinet Condition Assessment", "label": "Assessments", "col": 6}},
                {"type": "doctype", "data": {"name": "Customer Upgrade Request", "label": "Upgrades", "col": 6}},
                {"type": "report", "data": {"report_name": "Repair Summary", "doctype": "Repair Task Log", "col": 6}},
                {"type": "chart", "data": {"chart_name": "Open Repairs by Type", "col": 12}}
            ]
        }).insert(ignore_permissions=True)
        frappe.db.commit()