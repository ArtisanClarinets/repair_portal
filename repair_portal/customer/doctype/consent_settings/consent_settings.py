# Path: repair_portal/customer/doctype/consent_settings/consent_settings.py
# Date: 2025-09-30
# Version: 3.0.0
# Description: Consent Settings singleton - comprehensive automation for consent forms, templates, workflows, and field management
# Dependencies: frappe, frappe.model.document, frappe.custom.doctype.custom_field.custom_field

from __future__ import annotations

import re
from typing import Any

import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from frappe.model.document import Document

CONSENT_FORM_DT = "Consent Form"

_VALID_FIELDNAME = re.compile(r"^[a-z][a-z0-9_]{2,}$")

class ConsentSettings(Document):
    def validate(self):
        """Comprehensive validation of all settings and mappings."""
        self._validate_mapping_variables_unique()
        self._validate_linked_sources_unique_and_sane()
        self._validate_doctype_references()

    def on_update(self):
        """Auto-apply changes when settings are updated."""
        frappe.logger("consent_settings").info(f"Consent Settings updated by {frappe.session.user}")
        
        # Auto-apply linked sources when toggled
        if int(getattr(self, "apply_on_save", 0)) == 1:
            self.apply_linked_sources()
        
        # Ensure workflow exists and is updated
        self._ensure_consent_workflow()
        
        # Clear related caches
        self._clear_caches()

    def after_insert(self):
        """Initialize default settings after first creation."""
        self._create_default_templates()
        self._ensure_consent_workflow()

    # ------------------------------------------------------------------
    # Public API: callable from bench or client
    # ------------------------------------------------------------------
    @frappe.whitelist()
    def apply_linked_sources(self) -> dict[str, Any]:
        """Create or update Link custom fields on Consent Form per Linked Sources."""
        created, updated, skipped = [], [], []
        
        if not frappe.has_permission("Custom Field", "write"):
            frappe.throw(_("Insufficient permissions to create custom fields"))
        
        meta = frappe.get_meta(CONSENT_FORM_DT)

        for row in (self.linked_sources or []):
            if not getattr(row, "enabled", 0):
                skipped.append((row.fieldname or "", "disabled"))
                continue

            result = self._process_linked_source_row(row, meta)
            if result[0] == "created":
                created.append(result[1])
            elif result[0] == "updated":
                updated.append(result[1])
            else:
                skipped.append(result[1:])

        # Clear cache to reflect new fields immediately
        frappe.clear_cache(doctype=CONSENT_FORM_DT)
        
        return {
            "status": "success",
            "created": created, 
            "updated": updated, 
            "skipped": skipped,
            "message": f"Applied {len(created)} new fields, updated {len(updated)} fields, skipped {len(skipped)} fields"
        }

    @frappe.whitelist()
    def create_default_templates(self) -> dict[str, Any]:
        """Create standard consent templates if they don't exist."""
        return self._create_default_templates()

    @frappe.whitelist()
    def ensure_workflow(self) -> dict[str, Any]:
        """Ensure consent form workflow exists and is properly configured."""
        return self._ensure_consent_workflow()

    @frappe.whitelist()
    def get_available_variables(self) -> list[str]:
        """Return list of available template variables from mappings."""
        variables = []
        for mapping in (self.mappings or []):
            if mapping.variable_name and getattr(mapping, "enabled", 0):
                variables.append(mapping.variable_name)
        return sorted(variables)

    @frappe.whitelist()
    def validate_template_syntax(self, template_content: str) -> dict[str, Any]:
        """Validate Jinja template syntax and available variables."""
        try:
            from jinja2 import Environment, meta
            
            env = Environment()
            ast = env.parse(template_content)
            undefined_vars = meta.find_undeclared_variables(ast)
            available_vars = set(self.get_available_variables())
            
            missing_vars = undefined_vars - available_vars - {"date", "form"}
            
            return {
                "valid": len(missing_vars) == 0,
                "missing_variables": list(missing_vars),
                "available_variables": list(available_vars),
                "template_variables": list(undefined_vars)
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "missing_variables": [],
                "available_variables": self.get_available_variables(),
                "template_variables": []
            }
    # ------------------------------------------------------------------
    # Internal implementation methods
    # ------------------------------------------------------------------
    def _process_linked_source_row(self, row: Any, meta: Any) -> tuple[str, str, str]:
        """Process a single linked source row and create/update custom field."""
        fieldname = (row.fieldname or "").strip()
        label = (row.label or "").strip()
        options = (row.source_doctype or "").strip()
        insert_after = (row.insert_after or "consent_template").strip()

        # Validation
        if not fieldname or not _VALID_FIELDNAME.match(fieldname):
            return ("skipped", fieldname, "invalid fieldname")
        if not label:
            return ("skipped", fieldname, "missing label")
        if not options:
            return ("skipped", fieldname, "missing source_doctype")
        if not frappe.db.exists("DocType", options):
            return ("skipped", fieldname, f"source_doctype '{options}' does not exist")

        # If a standard field exists with same name, skip (avoid conflict)
        std_field = meta.get_field(fieldname)
        if std_field and not getattr(std_field, "is_custom_field", 0):
            return ("skipped", fieldname, "standard field exists")

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
            "description": getattr(row, "description", "") or f"Auto-generated link to {options}"
        }

        try:
            if cf_name:
                # Update existing custom field doc
                cf_doc = frappe.get_doc("Custom Field", cf_name)
                cf_doc.update(props)
                cf_doc.save(ignore_permissions=True)
                return ("updated", fieldname, "")
            else:
                # Create new custom field
                create_custom_field(CONSENT_FORM_DT, props, ignore_validate=False)
                return ("created", fieldname, "")
        except Exception as e:
            frappe.log_error(f"Error creating/updating custom field {fieldname}: {str(e)}")
            return ("skipped", fieldname, f"error: {str(e)}")

    def _create_default_templates(self) -> dict[str, Any]:
        """Create standard consent templates if they don't exist."""
        templates = [
            {
                "title": "Standard Privacy Consent",
                "consent_type": "Privacy",
                "content": """<h2>Privacy and Data Processing Consent</h2>
                <p>Date: {{ date }}</p>
                <p>Customer: {{ customer_name }}</p>
                
                <h3>Consent for Data Processing</h3>
                <p>I, {{ customer_name }}, hereby give my explicit consent for {{ company_name or "the company" }} 
                to process my personal data for the following purposes:</p>
                
                <ul>
                    <li>Service delivery and customer support</li>
                    <li>Communication regarding services and updates</li>
                    <li>Legal compliance and record keeping</li>
                </ul>
                
                <p>This consent can be withdrawn at any time by contacting us.</p>
                <p>Signature: ______________________</p>""",
                "required_fields": [
                    {"field_label": "Customer Name", "field_type": "Data", "default_value": ""},
                    {"field_label": "Company Name", "field_type": "Data", "default_value": "Artisan Clarinets"}
                ]
            },
            {
                "title": "Repair Service Consent",
                "consent_type": "Repair",
                "content": """<h2>Instrument Repair Service Agreement</h2>
                <p>Date: {{ date }}</p>
                <p>Customer: {{ customer_name }}</p>
                <p>Instrument: {{ instrument_description }}</p>
                
                <h3>Service Authorization</h3>
                <p>I authorize {{ company_name or "Artisan Clarinets" }} to perform repair services on my instrument 
                as described in the estimate. I understand:</p>
                
                <ul>
                    <li>Additional work may be required and will be discussed before proceeding</li>
                    <li>All work is performed by qualified technicians</li>
                    <li>I am responsible for pickup within 30 days of completion</li>
                </ul>
                
                <p>Estimated cost: {{ estimated_cost }}</p>
                <p>Signature: ______________________</p>""",
                "required_fields": [
                    {"field_label": "Customer Name", "field_type": "Data", "default_value": ""},
                    {"field_label": "Instrument Description", "field_type": "Data", "default_value": ""},
                    {"field_label": "Estimated Cost", "field_type": "Currency", "default_value": "0.00"},
                    {"field_label": "Company Name", "field_type": "Data", "default_value": "Artisan Clarinets"}
                ]
            }
        ]

        created = []
        for template_data in templates:
            if not frappe.db.exists("Consent Template", template_data["title"]):
                try:
                    template_doc = frappe.get_doc({
                        "doctype": "Consent Template",
                        "title": template_data["title"],
                        "consent_type": template_data["consent_type"],
                        "content": template_data["content"],
                        "is_active": 1,
                        "required_fields": template_data["required_fields"]
                    })
                    template_doc.insert(ignore_permissions=True)
                    created.append(template_data["title"])
                except Exception as e:
                    frappe.log_error(f"Error creating template {template_data['title']}: {str(e)}")

        return {"created_templates": created, "count": len(created)}

    def _ensure_consent_workflow(self) -> dict[str, Any]:
        """Ensure consent form workflow exists and is properly configured."""
        try:
            # Import the workflow installer
            from repair_portal.utils.install.install_consent_artifacts import (
                install_or_update_consent_artifacts,
            )
            result = install_or_update_consent_artifacts()
            return result
        except ImportError:
            frappe.log_error("Consent workflow installer not found")
            return {"status": "error", "message": "Workflow installer not available"}
        except Exception as e:
            frappe.log_error(f"Error installing consent workflow: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _clear_caches(self) -> None:
        """Clear relevant caches after settings changes."""
        frappe.clear_cache(doctype=CONSENT_FORM_DT)
        frappe.clear_cache(doctype="Consent Template")
        frappe.clear_cache(doctype="Consent Settings")

    def _validate_doctype_references(self) -> None:
        """Validate that all referenced DocTypes exist."""
        for mapping in (self.mappings or []):
            if mapping.source_doctype and not frappe.db.exists("DocType", mapping.source_doctype):
                frappe.throw(_("Source DocType '{0}' does not exist").format(mapping.source_doctype))
        
        for linked_source in (self.linked_sources or []):
            if linked_source.source_doctype and not frappe.db.exists("DocType", linked_source.source_doctype):
                frappe.throw(_("Source DocType '{0}' does not exist").format(linked_source.source_doctype))

    # ------------------------------------------------------------------
    # Internal validation helpers
    # ------------------------------------------------------------------
    def _validate_mapping_variables_unique(self) -> None:
        """Ensure mapping variable names are unique."""
        seen, dupes = set(), set()
        for m in (self.mappings or []):
            var = (m.variable_name or "").strip()
            if not var:
                frappe.throw(_("Each mapping row must have a Variable Name (snake_case)."))
            if not _VALID_FIELDNAME.match(var):
                frappe.throw(_("Invalid variable name '{0}'. Must be snake_case, start with letter, 3+ chars").format(var))
            if var in seen:
                dupes.add(var)
            else:
                seen.add(var)
        if dupes:
            frappe.throw(_("Duplicate mapping variables: {0}").format(", ".join(sorted(dupes))))

    def _validate_linked_sources_unique_and_sane(self) -> None:
        """Ensure linked source fieldnames are unique and valid."""
        seen_names, dupes = set(), set()
        for r in (self.linked_sources or []):
            fname = (r.fieldname or "").strip()
            if not fname:
                frappe.throw(_("Each linked source must have a fieldname (snake_case)."))
            if not _VALID_FIELDNAME.match(fname):
                frappe.throw(_("Invalid linked source fieldname: {0}").format(fname))
            if fname in seen_names:
                dupes.add(fname)
            else:
                seen_names.add(fname)
        if dupes:
            frappe.throw(_("Duplicate linked source fieldnames: {0}").format(", ".join(sorted(dupes))))


# Public API functions
@frappe.whitelist()
def get_consent_settings() -> dict[str, Any]:
    """Get consent settings with additional metadata."""
    if not frappe.db.exists("Consent Settings"):
        # Create singleton if it doesn't exist
        settings = frappe.get_doc({"doctype": "Consent Settings"})
        settings.insert(ignore_permissions=True)
    else:
        settings = frappe.get_single("Consent Settings")
    
    return {
        "settings": settings.as_dict(),
        "available_doctypes": _get_available_doctypes(),
        "available_fieldtypes": ["Data", "Text", "Int", "Float", "Currency", "Date", "Datetime", "Check", "Select"]
    }

@frappe.whitelist()
def validate_field_mapping(source_doctype: str, source_fieldname: str) -> dict[str, Any]:
    """Validate that a field mapping is valid."""
    if not frappe.db.exists("DocType", source_doctype):
        return {"valid": False, "error": f"DocType '{source_doctype}' does not exist"}
    
    meta = frappe.get_meta(source_doctype)
    field = meta.get_field(source_fieldname)
    
    if not field:
        return {"valid": False, "error": f"Field '{source_fieldname}' does not exist in '{source_doctype}'"}
    
    return {
        "valid": True,
        "field_info": {
            "fieldtype": field.fieldtype,
            "label": field.label,
            "options": field.options
        }
    }

def _get_available_doctypes() -> list[str]:
    """Get list of available DocTypes for field mappings."""
    return frappe.get_all("DocType", 
                         filters={"custom": 0, "is_child_table": 0}, 
                         fields=["name"], 
                         order_by="name",
                         pluck="name")
