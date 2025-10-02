# Path: repair_portal/patches/v15_03_player_profile_indexes.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Adds performance indexes to Player Profile DocType for optimized queries
# Dependencies: frappe

import frappe

def execute():
    """
    Add performance indexes to Player Profile table
    Idempotent: Safe to run multiple times
    """
    if not frappe.db.table_exists("Player Profile"):
        frappe.log_error("Player Profile table does not exist", "Index Patch Skipped")
        return

    try:
        # Add index on player_name for full-text search
        if not frappe.db.sql("""
            SELECT COUNT(*) FROM information_schema.statistics
            WHERE table_schema = %s
            AND table_name = 'tabPlayer Profile'
            AND index_name = 'player_name_index'
        """, (frappe.conf.db_name,))[0][0]:
            frappe.db.add_index("Player Profile", ["player_name"])
            frappe.db.commit()
            print("✓ Added index on player_name")
        else:
            print("✓ Index on player_name already exists")

        # Add index on primary_email for unique lookups
        if not frappe.db.sql("""
            SELECT COUNT(*) FROM information_schema.statistics
            WHERE table_schema = %s
            AND table_name = 'tabPlayer Profile'
            AND index_name = 'primary_email_index'
        """, (frappe.conf.db_name,))[0][0]:
            frappe.db.add_index("Player Profile", ["primary_email"])
            frappe.db.commit()
            print("✓ Added index on primary_email")
        else:
            print("✓ Index on primary_email already exists")

        # Add index on player_level for filtering/reporting
        if not frappe.db.sql("""
            SELECT COUNT(*) FROM information_schema.statistics
            WHERE table_schema = %s
            AND table_name = 'tabPlayer Profile'
            AND index_name = 'player_level_index'
        """, (frappe.conf.db_name,))[0][0]:
            frappe.db.add_index("Player Profile", ["player_level"])
            frappe.db.commit()
            print("✓ Added index on player_level")
        else:
            print("✓ Index on player_level already exists")

        # Add index on profile_status for workflow queries
        if not frappe.db.sql("""
            SELECT COUNT(*) FROM information_schema.statistics
            WHERE table_schema = %s
            AND table_name = 'tabPlayer Profile'
            AND index_name = 'profile_status_index'
        """, (frappe.conf.db_name,))[0][0]:
            frappe.db.add_index("Player Profile", ["profile_status"])
            frappe.db.commit()
            print("✓ Added index on profile_status")
        else:
            print("✓ Index on profile_status already exists")

        frappe.db.commit()
        print("✅ Player Profile indexes patch completed successfully")

    except Exception as e:
        frappe.log_error(f"Player Profile indexes patch failed: {str(e)}", "Index Patch Error")
        print(f"❌ Player Profile indexes patch failed: {str(e)}")
        raise
