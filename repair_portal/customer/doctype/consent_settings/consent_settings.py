# -*- coding: utf-8 -*-
# File: repair_portal/customer/doctype/consent_settings/consent_settings.py
# Version: v2.0.0 (2025-09-14)
from __future__ import annotations

import re
import frappe
from frappe.model.document import Document
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

CONSENT_FORM_DT = "Consent Form"

_VALID_FIELDNAME = re.compile(r"^[a-z][a-z0-9_]{2,}$")

class ConsentSettings(Document):
    def validate(self):
        self._validate_mapping_variables_unique()
        self._validate_linked_sources_unique_and_sane()

    def on_update(self):
        # Auto-apply when toggled
        if int(getattr(self, "apply_on_save", 0)) == 1:
            self.apply_linked_sources()

    # ------------------------------------------------------------------
    # Public: callable from bench or client
    # ------------------------------------------------------------------
    @frappe.whitelist()
    def apply_linked_sources(self):
        """Create or update Link custom fields on Consent Form per Linked Sources."""
        created, updated, skipped = [], [], []
        meta = frappe.get_meta(CONSENT_FORM_DT)

        for row in (self.linked_sources or []):
            if not getattr(row, "enabled", 0):
                skipped.append((row.fieldname or "", "disabled"))
                continue

            fieldname = (row.fieldname or "").strip()
            label = (row.label or "").strip()
            options = (row.source_doctype or "").strip()
            insert_after = (row.insert_after or "consent_template").strip()

            # Validation
            if not fieldname or not _VALID_FIELDNAME.match(fieldname):
                skipped.append((fieldname, "invalid fieldname"))
                continue
            if not label:
                skipped.append((fieldname, "missing label"))
                continue
            if not options:
                skipped.append((fieldname, "missing source_doctype"))
                continue
            if not frappe.db.exists("DocType", options):
                skipped.append((fieldname, f"source_doctype '{options}' does not exist"))
                continue

            # If a standard field exists with same name, skip (avoid conflict)
            std_field = meta.get_field(fieldname)
            if std_field and not getattr(std_field, "is_custom_field", 0):
                skipped.append((fieldname, "standard field exists"))
                continue

            # Check if Custom Field already exists
            cf_name = frappe.db.get_value(
                "Custom Field",
                {"dt": CONSENT_FORM_DT, "fieldname": fieldname},
                "name"
            )

            props = {
                "fieldtype": "Link",
                "label": label,
                "fieldname": fieldname,
                "options": options,
                "insert_after": insert_after,
                "reqd": int(getattr(row, "reqd", 0)),
                "read_only": int(getattr(row, "read_only", 0)),
                "hidden": int(getattr(row, "hidden", 0)),
                "in_list_view": int(getattr(row, "in_list_view", 0)),
                "depends_on": getattr(row, "depends_on", None) or "",
                "permlevel": int(getattr(row, "permlevel", 0)),
            }

            if cf_name:
                # Update existing custom field doc
                cf_doc = frappe.get_doc("Custom Field", cf_name)
                cf_doc.update(props)
                cf_doc.save(ignore_permissions=True)
                updated.append(fieldname)
            else:
                # Create new custom field
                create_custom_field(CONSENT_FORM_DT, props, ignore_validate=False)
                created.append(fieldname)

        # Clear cache to reflect new fields immediately
        frappe.clear_cache(doctype=CONSENT_FORM_DT)

        return {
            "created": created, "updated": updated, "skipped": skipped
        }

    # ------------------------------------------------------------------
    # Internal validation helpers
    # ------------------------------------------------------------------
    def _validate_mapping_variables_unique(self):
        seen, dupes = set(), set()
        for m in (self.mappings or []):
            var = (m.variable_name or "").strip()
            if not var:
                frappe.throw("Each mapping row must have a Variable Name (snake_case).")
            if var in seen:
                dupes.add(var)
            else:
                seen.add(var)
        if dupes:
            frappe.throw(f"Duplicate mapping variables: {', '.join(sorted(dupes))}")

    def _validate_linked_sources_unique_and_sane(self):
        seen_names, dupes = set(), set()
        for r in (self.linked_sources or []):
            fname = (r.fieldname or "").strip()
            if not fname:
                frappe.throw("Each linked source must have a fieldname (snake_case).")
            if not _VALID_FIELDNAME.match(fname):
                frappe.throw(f"Invalid linked source fieldname: {fname}")
            if fname in seen_names:
                dupes.add(fname)
            else:
                seen_names.add(fname)
        if dupes:
            frappe.throw(f"Duplicate linked source fieldnames: {', '.join(sorted(dupes))}")
