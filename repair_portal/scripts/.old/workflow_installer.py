# relative path: repair_portal/customer/workflow_installer.py
# updated: 2025-06-28
# version: 1.2.0
# purpose: Traverse app and insert all workflows on migrate if not present, with validation

import json
import os

import frappe

APP_WORKFLOW_ROOT = "/opt/frappe/erp-bench/apps/repair_portal/repair_portal/"


def ensure_all_workflows():
	"""
	Traverse the app directory and ensure all workflows are loaded in the DB.
	"""
	for dirpath, dirnames, filenames in os.walk(APP_WORKFLOW_ROOT):
		if os.path.basename(dirpath) == "workflow":
			for fname in filenames:
				if fname.endswith(".json"):
					workflow_path = os.path.join(dirpath, fname)
					insert_workflow_if_valid(workflow_path)


def insert_workflow_if_valid(workflow_path):
	try:
		with open(workflow_path) as f:
			data = json.load(f)

		workflow_name = data.get("name")
		doc_type = data.get("document_type")
		workflow_state_field = data.get("workflow_state_field")

		if not workflow_name or not doc_type:
			frappe.logger().warning(f"Skipping workflow (missing name or document_type): {workflow_path}")
			return

		if not frappe.db.exists("DocType", {"name": doc_type}):
			frappe.logger().warning(
				f"Skipping workflow '{workflow_name}' because DocType '{doc_type}' does not exist."
			)
			return

		# Check that the workflow_state_field exists
		field_exists = frappe.db.exists("DocField", {"parent": doc_type, "fieldname": workflow_state_field})
		if not field_exists:
			frappe.logger().warning(
				f"Skipping workflow '{workflow_name}' because field '{workflow_state_field}' does not exist in DocType '{doc_type}'."
			)
			return

		if frappe.db.exists("Workflow", {"name": workflow_name}):
			frappe.logger().info(f"Workflow '{workflow_name}' already exists.")
			return

		workflow = frappe.get_doc(data)
		workflow.insert(ignore_permissions=True)
		frappe.db.commit()
		print(f"Inserted workflow '{workflow_name}' from {workflow_path}")
		frappe.logger().info(f"Inserted workflow '{workflow_name}' from {workflow_path}")

	except Exception as e:
		frappe.logger().error(f"Error inserting workflow from {workflow_path}: {e}")
		print(f"Error inserting workflow from {workflow_path}: {e}")
