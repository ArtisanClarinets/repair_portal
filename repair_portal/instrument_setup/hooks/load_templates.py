# File Header Template
# Relative Path: repair_portal/instrument_setup/hooks/load_templates.py
# Last Updated: 2025-07-30
# Version: v1.1
# Purpose: Load all JSON setup template files from the instrument_setup/hooks/templates directory and insert/update them in Frappe.
# Dependencies: Frappe ORM, Setup Template Doctype

import json
import os

import frappe


def load_setup_templates():
	"""
	Load all Setup Template JSON files from the instrument_setup/hooks/templates directory
	and insert/update them into the Frappe database.

	This function is intended to be hooked into `after_install` in hooks.py.
	"""
	try:
		# Resolve absolute path to the templates directory
		base_path = os.path.join(
			os.path.dirname(__file__),  # /hooks/
			"templates",  # /hooks/templates/
		)
		base_path = os.path.abspath(base_path)

		if not os.path.exists(base_path):
			frappe.log_error(f"Template directory not found: {base_path}", "Setup Template Loader")
			return

		# Iterate over all .json files in the templates directory
		for file_name in os.listdir(base_path):
			if not file_name.endswith(".json"):
				continue

			file_path = os.path.join(base_path, file_name)

			# Read and parse JSON file
			with open(file_path, encoding="utf-8") as f:
				try:
					template_data = json.load(f)
				except json.JSONDecodeError as e:
					frappe.log_error(f"Invalid JSON in {file_name}: {str(e)}", "Setup Template Loader")
					continue

			template_name = template_data.get("name")
			if not template_name:
				frappe.log_error(f"Missing 'name' field in {file_name}", "Setup Template Loader")
				continue

			try:
				# Check if template already exists
				if frappe.db.exists("Setup Template", template_name):
					# Update existing template
					doc = frappe.get_doc("Setup Template", template_name)
					doc.update(template_data)
					doc.save(ignore_permissions=True)
					frappe.logger().info(f"🔄 Updated Setup Template: {template_name}")
				else:
					# Insert new template
					doc = frappe.get_doc(template_data)
					doc.insert(ignore_permissions=True)
					frappe.logger().info(f"✅ Inserted Setup Template: {template_name}")

			except Exception as e:
				frappe.log_error(
					f"Failed to insert/update {template_name}: {str(e)}", "Setup Template Loader"
				)

		frappe.db.commit()

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Setup Template Loader Failed")
