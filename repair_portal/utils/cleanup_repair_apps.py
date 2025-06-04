import frappe

def run():
    apps_to_clean = ["repair_portal", "clarinet_repair_portal"]
    doctypes_to_clean = [
        "Module Def", "DocType", "Custom Field", "Custom Script",
        "Report", "Page", "Workspace", "Web Page", "Web Form"
    ]

    for doctype in doctypes_to_clean:
        for app in apps_to_clean:
            try:
                docs = frappe.get_all(doctype, filters={"app_name": app})
                for doc in docs:
                    frappe.delete_doc(doctype, doc.name, force=True)
                    print(f"Deleted {doctype}: {doc.name}")
            except Exception as e:
                print(f"Skip {doctype} for {app}: {e}")

    for app in apps_to_clean:
        modules = frappe.get_all("Module Def", filters={"app_name": app})
        for module in modules:
            module_name = module.name
            orphaned = frappe.get_all("DocType", filters={"module": module_name})
            for doc in orphaned:
                try:
                    frappe.delete_doc("DocType", doc.name, force=True)
                    print(f"Deleted orphaned DocType: {doc.name}")
                except Exception as e:
                    print(f"Skip orphan {doc.name}: {e}")

    frappe.db.commit()
    print("✅ Cleanup complete.")