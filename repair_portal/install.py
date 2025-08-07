# repair_portal/install.py
import sys
import frappe

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