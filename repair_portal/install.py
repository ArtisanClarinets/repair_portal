# repair_portal/install.py
import sys
import traceback

import frappe

#############################################################################
# Run ERPNext Setup Verification                                            #
# Ensures the ERPNext Initial Setup has been completed via the Desk UI      #
# Date: 2025-07-18                                                          #
# Version: 1.0                                                              #
#############################################################################


def _is_setup_complete() -> bool:
	db = frappe.db  # type: ignore

	# 1️⃣  Wizard flag (v14+)
	if db.table_exists("System Settings") and db.has_column("System Settings", "setup_complete"):
		if db.get_single_value("System Settings", "setup_complete"):
			return True

	# 2️⃣  Fallback: any Company exists
	return db.table_exists("Company") and db.count("Company") > 0


def check_setup_complete(*args):
	if _is_setup_complete():
		return  # all good

	site = frappe.local.site  # type: ignore
	msg = (
		f"\n🛑  ERPNext setup wizard is *not finished* for site **{site}**.\n"
		f"➡️  Log in as *Administrator*, complete the wizard,\n"
		f"   then run:\n"
		f"   bench --site {site} install-app repair_portal\n"
	)

	# optional – make absolutely sure no open tx is left hanging
	frappe.db.rollback()  # type: ignore

	# clean exit: message only, no stack trace
	sys.exit(msg)

	# If we reach here, it means the setup is complete
	print(f"✅  ERPNext setup wizard is *finished* for site **{site}**.")


#############################################################################
# create/update Item Groups from JSON under scripts/schemas.                #
# Safe & idempotent:                                                        #
#   - upserts Item Groups only (no deletes),                                #
#   - prints to console and logs to frappe logger,                          #
#   - quietly skips if the folder/file isn't present.                       #
#   - can be re-run as needed (e.g. after patches).                         #
# Date: 2025-08-10                                                          #
# Version: 1.0                                                              #
#############################################################################
def seed_item_groups_after_migrate():
	"""Hook: create/update Item Groups from JSON under scripts/schemas.

	Safe & idempotent:
	  - upserts Item Groups only (no deletes),
	  - prints to console and logs to frappe logger,
	  - quietly skips if the folder/file isn't present.
	"""
	import traceback

	from .scripts.item_group_loader import load_item_groups_from_default_schemas

	try:
		print("🎼 Seeding Item Groups from scripts/schemas …")
		frappe.logger().info("Seeding Item Groups from scripts/schemas …")
		load_item_groups_from_default_schemas()  # auto-detects Item Group JSON
		print("✅ Item Group seeding finished.")
		frappe.logger().info("Item Group seeding finished.")
	except (FileNotFoundError, RuntimeError) as e:
		# Missing folder or file? Don't fail migrate—just inform and continue.
		msg = f"Skipping Item Group seeding: {e}"
		print(f"ℹ️  {msg}")
		frappe.logger().info(msg)
	except Exception as e:
		# Unexpected error: log and continue (don’t break migrate by default)
		frappe.db.rollback()
		print(f"\033[91m❌ Item Group seeding failed: {e}\033[0m")
		frappe.logger().error(f"Item Group seeding failed: {e}")
		frappe.logger().error(traceback.format_exc())
		frappe.log_error(title="Item Group Seeding Failed", message=traceback.format_exc())
		# If you prefer to fail the migration on errors, uncomment:
		# raise


#############################################################################
# in repair_portal/install.py
def seed_all_from_schemas():
	from .scripts.doctype_loader import load_from_default_schemas

	try:
		print("🌱 Seeding doctypes from schemas …")
		load_from_default_schemas()
		print("✅ Seeding complete.")
	except Exception as e:
		frappe.db.rollback()
		print(f"\033[91m❌ Seeding failed: {e}\033[0m")
		frappe.log_error(title="Schema Seeding Failed", message=traceback.format_exc())
		# raise  # uncomment if you want migrate to fail on errors


#############################################################################


#############################################################################
# Audit: Naming Series after migrate                                        #
# Runs the naming_audit and prints to console + logs. Does NOT block        #
# migrate unless REPAIR_PORTAL_FAIL_ON_NAMING_AUDIT=1                       #
# Date: 2025-08-10                                                          #
# Version: 1.1                                                              #
#############################################################################
import os


def audit_naming_series_after_migrate():
	"""Hook target for after_migrate: run naming series audit."""
	# ✅ Correct import path (no double 'repair_portal')
	from repair_portal.scripts import naming_audit

	# Optional structured logs if you added logger.py
	try:
		from repair_portal.logger import get_logger

		log = get_logger("naming_audit")
	except Exception:
		log = None

	try:
		print("🔎 Auditing naming series …")
		if log:
			log.info("Starting naming series audit (after_migrate)")
		naming_audit.run()  # prints full report
		print("✅ Naming series audit complete.")
		if log:
			log.info("Naming series audit complete.")
	except Exception as e:
		# show full traceback in console
		print(f"\033[91m❌ Naming series audit failed: {e}\033[0m")
		traceback.print_exc()
		frappe.log_error(title="Naming Series Audit Failed", message=traceback.format_exc())
		if log:
			log.exception("Naming series audit failed")
		# optional: fail migration only when explicitly enabled
		if str(os.environ.get("REPAIR_PORTAL_FAIL_ON_NAMING_AUDIT", "0")).lower() in (
			"1",
			"true",
			"yes",
			"on",
		):
			raise
		try:
			frappe.db.rollback()
		except Exception:
			pass
