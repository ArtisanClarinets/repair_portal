# Path: repair_portal/repair_portal/customer/doctype/consent_linked_source/consent_linked_source.py
# Date: 2025-01-27
# Version: 3.1.0
# Description: Child table for consent linked sources with validation, source tracking, and relationship management
# Dependencies: frappe.model.document

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.model.document import Document


class ConsentLinkedSource(Document):
    """Child table for Consent Linked Source with comprehensive source tracking and validation."""
    
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        enabled: DF.Check
        label: DF.Data
        fieldname: DF.Data
        source_doctype: DF.Link
        insert_after: DF.Data
        reqd: DF.Check
        read_only: DF.Check
        hidden: DF.Check
        in_list_view: DF.Check
        permlevel: DF.Int
        depends_on: DF.Data
        description: DF.SmallText
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
    # end: auto-generated types
    
    def validate(self) -> None:
        """Comprehensive validation for linked source configuration."""
        self._validate_required_fields()
        self._validate_source_configuration()
        self._validate_doctype_references()
        self._validate_field_configuration()
        self._set_defaults()
        
    def _validate_required_fields(self) -> None:
        """Validate all required fields are present."""
        required_fields = {
            'label': 'Link Field Label',
            'fieldname': 'Link Fieldname',
            'source_doctype': 'Source DocType'
        }
        
        missing = []
        for field, label in required_fields.items():
            if not self.get(field):
                missing.append(label)
        
        if missing:
            frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))
    
    def _validate_source_configuration(self) -> None:
        """Validate source configuration logic."""
        # Fieldname should be valid snake_case identifier
        if self.fieldname:
            import re
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.fieldname):
                frappe.throw(_("Fieldname must be a valid identifier: {0}").format(self.fieldname))
            
            # Convert to snake_case convention
            self.fieldname = frappe.scrub(self.fieldname)
        
        # Label should be meaningful
        if self.label and len(self.label.strip()) < 2:
            frappe.throw(_("Label must be at least 2 characters long"))
    
    def _validate_doctype_references(self) -> None:
        """Validate that referenced DocTypes exist."""
        if self.source_doctype and not frappe.db.exists("DocType", self.source_doctype):
            frappe.throw(_("Source DocType does not exist: {0}").format(self.source_doctype))
    
    def _validate_field_configuration(self) -> None:
        """Validate field configuration consistency."""
        # Validate permlevel is reasonable
        if self.permlevel and (self.permlevel < 0 or self.permlevel > 9):
            frappe.throw(_("Permlevel must be between 0 and 9"))
        
        # Validate depends_on syntax if provided
        if self.depends_on:
            # Basic validation - should not be empty and should not contain dangerous code
            if not self.depends_on.strip():
                self.depends_on = None
            elif any(keyword in self.depends_on.lower() for keyword in ['import ', 'exec(', 'eval(']):
                frappe.throw(_("Depends On expression contains potentially dangerous code"))
    
    def _set_defaults(self) -> None:
        """Set default values for various fields."""
        # Default enabled to true for new sources
        if not hasattr(self, 'enabled') or self.enabled is None:
            self.enabled = 1
        
        # Default insert_after if not specified
        if not self.insert_after:
            self.insert_after = "consent_template"
        
        # Default permlevel
        if not self.permlevel:
            self.permlevel = 0
        
        # Auto-generate description if missing
        if not self.description and self.label and self.source_doctype:
            self.description = f"Link to {self.source_doctype} - {self.label}"
    
    def get_field_definition(self) -> dict[str, Any]:
        """Generate field definition for dynamic field creation."""
        return {
            'fieldname': self.fieldname,
            'label': self.label,
            'fieldtype': 'Link',
            'options': self.source_doctype,
            'reqd': int(self.reqd or 0),
            'read_only': int(self.read_only or 0),
            'hidden': int(self.hidden or 0),
            'in_list_view': int(self.in_list_view or 0),
            'permlevel': self.permlevel or 0,
            'depends_on': self.depends_on or None,
            'description': self.description or f"Link to {self.source_doctype}",
            'insert_after': self.insert_after or 'consent_template'
        }
    
    def get_source_value(self, source_doc_name: str | None = None, field_name: str | None = None) -> Any:
        """Retrieve value from the linked source document."""
        if not self.enabled or not source_doc_name:
            return None
        
        try:
            # Default to 'name' field if no specific field requested
            if not field_name:
                field_name = 'name'
            
            value = frappe.db.get_value(
                self.source_doctype,
                source_doc_name,
                field_name
            )
            
            return value
            
        except Exception as e:
            frappe.log_error(f"Failed to get source value: {str(e)}")
            return None
    
    def test_source(self, test_doc_name: str | None = None) -> dict[str, Any]:
        """Test the source configuration with a sample document."""
        result = {
            'success': False,
            'value': None,
            'error': None,
            'warnings': []
        }
        
        try:
            if not test_doc_name and self.source_doctype:
                # Get a sample document for testing
                sample_docs = frappe.get_all(
                    self.source_doctype,
                    limit=1,
                    fields=['name']
                )
                if sample_docs:
                    test_doc_name = sample_docs[0].name
                else:
                    result['warnings'].append(f"No sample documents found in {self.source_doctype}")
                    return result
            
            if test_doc_name:
                value = self.get_source_value(test_doc_name)
                result['value'] = value
                result['success'] = True
                
                if value is None:
                    result['warnings'].append("Source returned None - check document exists")
                
            else:
                result['warnings'].append("No source document provided for testing")
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    @staticmethod
    def get_active_sources(parent_doctype: str, parent_name: str) -> list[ConsentLinkedSource]:
        """Get all active linked sources for a parent document."""
        return frappe.get_all(
            'Consent Linked Source',
            filters={
                'parent': parent_name,
                'parenttype': parent_doctype,
                'enabled': 1
            },
            fields=['*'],
            order_by='fieldname'
        )
    
    @staticmethod
    def create_dynamic_fields(target_meta: Any, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Create dynamic field definitions from linked sources."""
        field_definitions = []
        
        for source_data in sources:
            try:
                source = frappe.get_doc('Consent Linked Source', source_data.get('name'))
                field_def = source.get_field_definition()
                field_definitions.append(field_def)
                
            except Exception as e:
                frappe.log_error(f"Failed to create field definition from source: {str(e)}")
        
        return field_definitions