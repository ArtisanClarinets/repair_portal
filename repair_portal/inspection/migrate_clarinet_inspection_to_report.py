# repair_portal/inspection/migrate_clarinet_inspection_to_report.py
# Date Updated: 2025-06-30
# Version: 1.0
# Purpose: One-time script to migrate all Clarinet Inspection records to Inspection Report DocType, maintaining full data lineage

import csv

import frappe


def migrate_all_clarinet_inspections():
	migrated = []
	clarinet_inspections = frappe.get_all(
		"Clarinet Inspection",
		fields=[
			"name",
			"intake",
			"inspection_date",
			"technician",
			"preliminary_estimate",
			"status",
		],
	)

	for ci in clarinet_inspections:
		# Lookup Intake fields for mapping instrument/customer if possible
		intake = frappe.get_doc("Clarinet Intake", ci.intake) if ci.intake else None
		instrument_id = getattr(intake, "instrument_id", None)
		customer_name = getattr(intake, "customer_name", None)

		ir = frappe.new_doc("Inspection Report")
		ir.inspection_date = ci.inspection_date
		ir.instrument_id = instrument_id or ""
		ir.customer_name = customer_name or ""
		ir.inspection_type = "Clarinet Intake"
		ir.status = unify_status(ci.status)
		ir.preliminary_estimate = ci.preliminary_estimate
		ir.clarinet_intake_ref = ci.intake
		ir.legacy_clarinet_inspection_id = ci.name
		# Copy findings if available (manual mapping may be needed for sub-tables)
		# Add more here if needed
		ir.insert(ignore_permissions=True)
		migrated.append(
			{
				"legacy": ci.name,
				"new": ir.name,
				"intake": ci.intake,
				"instrument_id": instrument_id,
				"customer_name": customer_name,
				"status": ci.status,
			}
		)

	# Save mapping to CSV
	with open("/tmp/clarinet_inspection_migration_map.csv", "w", newline="") as csvfile:
		writer = csv.DictWriter(
			csvfile,
			fieldnames=["legacy", "new", "intake", "instrument_id", "customer_name", "status"],
		)
		writer.writeheader()
		writer.writerows(migrated)

	print(
		f"Migrated {len(migrated)} Clarinet Inspections. Mapping CSV at /tmp/clarinet_inspection_migration_map.csv"
	)


def unify_status(status):
	status_map = {
		"Pending": "Scheduled",
		"Awaiting Customer Approval": "Pending Review",
		"Pass": "Passed",
		"Fail": "Failed",
		"Passed": "Passed",
		"Failed": "Failed",
	}
	return status_map.get(status, status)


if __name__ == "__main__":
	migrate_all_clarinet_inspections()
