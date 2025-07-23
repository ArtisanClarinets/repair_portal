# File Header Template
# Relative Path: repair_portal/patches/migrate_photo_attachments.py
# Last Updated: 2025-07-22
# Version: v1.0
# Purpose: Migrate data from deprecated image doctypes to Instrument Media
# Dependencies: Instrument Media, Instrument Photo, Image Log Entry

import frappe

def execute():
    logger = frappe.logger("patches")
    moved = 0

    try:
        # Migrate Instrument Photo
        photos = frappe.get_all("Instrument Photo", fields=["image", "label", "notes", "parent", "parentfield", "parenttype"])
        for p in photos:
            frappe.get_doc({
                "doctype": "Instrument Media",
                "parent": p.parent,
                "parentfield": p.parentfield,
                "parenttype": p.parenttype,
                "media_file": p.image,
                "media_title": p.label,
                "description": p.notes,
                "media_type": "Photo"
            }).insert()
            moved += 1

        # Migrate Image Log Entry
        logs = frappe.get_all("Image Log Entry", fields=["image", "comment", "parent", "parentfield", "parenttype"])
        for l in logs:
            frappe.get_doc({
                "doctype": "Instrument Media",
                "parent": l.parent,
                "parentfield": l.parentfield,
                "parenttype": l.parenttype,
                "media_file": l.image,
                "media_title": l.comment or "Logged Image",
                "media_type": "Photo"
            }).insert()
            moved += 1

        frappe.db.commit()
        logger.info(f"✅ Migrated {moved} media entries to Instrument Media.")

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Photo Migration Failed")
        logger.error(f"❌ Migration failed: {str(e)}")