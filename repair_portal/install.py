# repair_portal/install.py
import sys
import frappe


#############################################################################
# Run ERPNext Setup Verification                                            #
# Ensures the ERPNext Initial Setup has been completed via the Desk UI      #
# Date: 2025-07-18                                                          #
# Version: 1.0                                                              #
#############################################################################

def _is_setup_complete() -> bool:
    db = frappe.db # type: ignore

    # 1️⃣  Wizard flag (v14+)
    if db.table_exists("System Settings") and db.has_column(
        "System Settings", "setup_complete"
    ):
        if db.get_single_value("System Settings", "setup_complete"):
            return True

    # 2️⃣  Fallback: any Company exists
    return db.table_exists("Company") and db.count("Company") > 0


def check_setup_complete(*args):
    if _is_setup_complete():
        return  # all good

    site = frappe.local.site # type: ignore
    msg = (
        f"\n🛑  ERPNext setup wizard is *not finished* for site **{site}**.\n"
        f"➡️  Log in as *Administrator*, complete the wizard,\n"
        f"   then run:\n"
        f"   bench --site {site} install-app repair_portal\n"
    )

    # optional – make absolutely sure no open tx is left hanging
    frappe.db.rollback() # type: ignore

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
    from .scripts.item_group_loader import load_item_groups_from_default_schemas
    import traceback

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
