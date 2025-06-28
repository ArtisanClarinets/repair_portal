import frappe
import os
import json

def insert_workflows_from_json():
    # Get the base directory of your app
    app_base_path = os.path.join(frappe.get_app_path("repair_portal"))
    doctype_dir = os.path.join(app_base_path, "repair_portal")

    # Traverse all directories and files within the app
    for root, dirs, files in os.walk(doctype_dir):
        for file in files:
            if file.endswith(".json"):  # Check if the file is a JSON file
                file_path = os.path.join(root, file)

                # Read the JSON file
                with open(file_path, 'r') as f:
                    try:
                        data = json.load(f)

                        # Check if the doctype key contains "Workflow"
                        if "doctype" in data and "Workflow" in data["doctype"]:
                            # Insert Workflow into the database
                            insert_workflow(data)

                    except Exception as e:
                        frappe.log_error(f"Error loading {file_path}: {str(e)}")

def insert_workflow(data):
    try:
        # Check if the workflow already exists in the database
        existing_workflow = frappe.get_all("Workflow", filters={"workflow_name": data.get("name")})
        if not existing_workflow:
            # If not, insert a new workflow
            workflow = frappe.get_doc({
                "doctype": "Workflow",
                "workflow_name": data.get("name"),
                "module": data.get("module"),
                "is_standard": data.get("is_standard", 0),
                "sync_on_migrate": data.get("sync_on_migrate", 0),
                "doc_type": data.get("doc_type"),
                "is_active": data.get("is_active", 1),
                "states": data.get("states", [])
            })
            workflow.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"Inserted Workflow: {data.get('name')}")
        else:
            print(f"Workflow {data.get('name')} already exists.")
    except Exception as e:
        frappe.log_error(f"Error inserting workflow {data.get('name')}: {str(e)}")

def execute():
    insert_workflows_from_json()

