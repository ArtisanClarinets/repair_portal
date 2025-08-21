#!/usr/bin/env python3
"""
Reload ALL .json files in the app recursively.
"""

import os

import frappe

APP_PATH = "/opt/frappe/erp-bench/apps/repair_portal/repair_portal"


def reload_all_jsons():
	"""
	Walk the app directory, find all *.json files, and reload them.
	"""
	print("🔄 Reloading ALL .json definitions in repair_portal...")

	for dirpath, dirnames, filenames in os.walk(APP_PATH):
		for filename in filenames:
			if filename.endswith(".json"):
				relative_path = os.path.relpath(os.path.join(dirpath, filename), APP_PATH)
				parts = relative_path.split(os.sep)

				if len(parts) == 4:
					module = parts[0]
					doctype = parts[1]
					docname = parts[2]

					json_path = os.path.join(dirpath, filename)

					if filename == f"{docname}.json":
						try:
							#    print(f"🔹 Reloading module='{module}' doctype='{doctype}' docname='{docname}'")
							frappe.reload_doc(module, doctype, docname)
						except Exception as e:
							frappe.logger().error(f"❌ Failed reloading {module}/{doctype}/{docname}: {e}")
							print(f"❌ Failed reloading {module}/{doctype}/{docname}: {e}")


#    print("✅ All reload attempts completed.")
