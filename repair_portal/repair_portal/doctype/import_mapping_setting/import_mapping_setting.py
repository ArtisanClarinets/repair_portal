# File Header Template
# Relative Path: repair_portal/repair_portal/doctype/import_mapping_setting/import_mapping_setting.py
# Last Updated: 2025-07-28
# Version: v1.0
# Purpose: Server-side logic for Import Mapping Setting; ensures unique mapping_name + target_doctype, provides API for fetching DocType fields.
# Dependencies: frappe, Repair Portal, Import Mapping Setting Field

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import cint
from functools import lru_cache

class ImportMappingSetting(Document):
    """Controller for Import Mapping Setting DocType."""
    def validate(self):
        """Ensure mapping_name + target_doctype combo is unique."""
        if frappe.db.exists({
            "doctype": self.doctype,
            "mapping_name": self.mapping_name,
            "target_doctype": self.target_doctype,
            "name": ["!=", self.name]
        }):
            frappe.throw(_("A mapping with name '{0}' already exists for {1}.")
                         .format(self.mapping_name, self.target_doctype))

@frappe.whitelist(allow_guest=False)
@lru_cache(maxsize=32)
def get_fields_for_doctype(doctype: str) -> list:
    """
    Return all fields for `doctype`, sorted with required fields first.
    Caches up to 32 distinct doctypes per process.
    Args:
        doctype (str): Target DocType
    Returns:
        list: List of dicts with fieldname, label, reqd
    Raises:
        frappe.DoesNotExistError: If doctype does not exist.
    """
    try:
        if not frappe.db.exists("DocType", doctype):
            frappe.throw(_("DocType {0} not found").format(doctype), frappe.DoesNotExistError)
        meta = frappe.get_meta(doctype)
        fields = []
        for df in meta.fields:
            if df.fieldtype in ("Section Break", "Column Break", "HTML", "Button", "Table"):
                continue
            fields.append({
                "fieldname": df.fieldname,
                "label": df.label,
                "reqd": cint(df.reqd)
            })
        fields.sort(key=lambda f: (-f["reqd"], f["label"].lower()))
        return fields
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "ImportMappingSetting.get_fields_for_doctype")
        frappe.throw(_("Failed to fetch fields for {0}: {1}").format(doctype, str(e)))
