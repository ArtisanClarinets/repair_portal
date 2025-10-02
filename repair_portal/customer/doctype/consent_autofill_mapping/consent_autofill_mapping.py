# Path: repair_portal/repair_portal/customer/doctype/consent_autofill_mapping/consent_autofill_mapping.py
# Date: 2025-01-27
# Version: 3.1.0
# Description: Child table for consent autofill mappings with validation, field resolution, and automatic value retrieval
# Dependencies: frappe.model.document, frappe.utils

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.model.document import Document


class ConsentAutofillMapping(Document):
    """Child table for Consent Autofill Mapping with comprehensive field mapping and validation."""
    
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        enabled: DF.Check
        variable_name: DF.Data
        source_doctype: DF.Link
        form_link_field: DF.Data
        source_fieldname: DF.Data
        default_value: DF.Data
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
    # end: auto-generated types
    
    def validate(self) -> None:
        """Comprehensive validation for autofill mapping configuration."""
        self._validate_required_fields()
        self._validate_mapping_configuration()
        self._validate_doctype_references()
        self._validate_field_compatibility()
        self._validate_circular_references()
        self._set_defaults()
        
    def _validate_required_fields(self) -> None:
        """Validate all required fields are present."""
        if not self.variable_name:
            frappe.throw(_("Variable Name is required"))
    
    def _validate_mapping_configuration(self) -> None:
        """Validate mapping configuration logic."""
        # Variable name should be valid Python identifier
        if self.variable_name:
            import re
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.variable_name):
                frappe.throw(_("Variable Name must be a valid Python identifier: {0}").format(self.variable_name))
            
            # Convert to snake_case convention
            self.variable_name = frappe.scrub(self.variable_name)
        
        # Either link field or direct value must be configured
        if not self.form_link_field and not self.default_value:
            frappe.throw(_("Either Form Link Field or Default Value must be specified"))
        
        # If using link field, validate the configuration
        if self.form_link_field and not self.source_doctype:
            frappe.throw(_("Source DocType is required when using Form Link Field"))
    
    def _validate_doctype_references(self) -> None:
        """Validate that referenced DocTypes exist."""
        # Check source DocType exists
        if self.source_doctype and not frappe.db.exists("DocType", self.source_doctype):
            frappe.throw(_("Source DocType does not exist: {0}").format(self.source_doctype))
    
    def _validate_field_compatibility(self) -> None:
        """Validate field compatibility between source and target."""
        if not self.source_doctype or not self.source_fieldname:
            return
        
        # Check source field exists
        source_meta = frappe.get_meta(self.source_doctype)
        source_field = source_meta.get_field(self.source_fieldname)
        
        if not source_field:
            frappe.throw(_("Source field '{0}' does not exist in DocType '{1}'").format(
                self.source_fieldname, self.source_doctype))
    
    def _validate_circular_references(self) -> None:
        """Check for circular references in mapping configuration."""
        if not self.form_link_field or not self.parent:
            return
        
        # Get parent document
        try:
            frappe.get_doc(self.parenttype, self.parent)
            
            # Check if the link field exists on the parent
            parent_meta = frappe.get_meta(self.parenttype)
            link_field = parent_meta.get_field(self.form_link_field)
            
            if not link_field:
                frappe.throw(_("Form Link Field '{0}' does not exist in {1}").format(
                    self.form_link_field, self.parenttype))
            
            # Validate link field points to correct DocType
            if link_field.options != self.source_doctype:
                frappe.throw(_("Form Link Field '{0}' points to '{1}', but Source DocType is '{2}'").format(
                    self.form_link_field, link_field.options, self.source_doctype))
            
        except Exception:
            # Don't fail validation if parent doesn't exist yet (new document)
            pass
    
    def _set_defaults(self) -> None:
        """Set default values for various fields."""
        # Default enabled to true for new mappings
        if not hasattr(self, 'enabled') or self.enabled is None:
            self.enabled = 1
    
    def get_mapped_value(self, source_doc_name: str | None = None) -> Any:
        """Retrieve the mapped value from source document."""
        if not self.enabled:
            return self.default_value
        
        if not source_doc_name:
            return self.default_value
        
        try:
            # Get value from source document
            value = frappe.db.get_value(
                self.source_doctype,
                source_doc_name,
                self.source_fieldname
            )
            
            if value is None:
                return self.default_value
            
            return value
            
        except Exception as e:
            frappe.log_error(f"Failed to get mapped value: {str(e)}")
            return self.default_value
    
    def test_mapping(self, test_doc_name: str | None = None) -> dict[str, Any]:
        """Test the mapping configuration with a sample document."""
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
                value = self.get_mapped_value(test_doc_name)
                result['value'] = value
                result['success'] = True
                
                if value is None:
                    result['warnings'].append("Mapping returned None - check field exists and has value")
                
            else:
                result['value'] = self.default_value
                result['success'] = True
                result['warnings'].append("Using default value - no source document provided")
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    @staticmethod
    def get_active_mappings(parent_doctype: str, parent_name: str) -> list[ConsentAutofillMapping]:
        """Get all active mappings for a parent document."""
        return frappe.get_all(
            'Consent Autofill Mapping',
            filters={
                'parent': parent_name,
                'parenttype': parent_doctype,
                'enabled': 1
            },
            fields=['*'],
            order_by='variable_name'
        )
    
    @staticmethod
    def apply_mappings(target_doc: Document, mappings: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Apply all active mappings to a target document."""
        if not mappings:
            mappings = ConsentAutofillMapping.get_active_mappings(
                target_doc.doctype, target_doc.name
            )
        
        results = {
            'applied_count': 0,
            'failed_count': 0,
            'warnings': [],
            'details': []
        }
        
        for mapping_data in mappings:
            try:
                mapping = frappe.get_doc('Consent Autofill Mapping', mapping_data.get('name'))
                
                # Get source document name from link field
                source_doc_name = None
                if mapping.form_link_field:
                    source_doc_name = getattr(target_doc, mapping.form_link_field, None)
                
                # Get mapped value
                value = mapping.get_mapped_value(source_doc_name)
                
                # Apply to target document
                if hasattr(target_doc, mapping.variable_name):
                    setattr(target_doc, mapping.variable_name, value)
                    results['applied_count'] += 1
                    results['details'].append(f"Applied {mapping.variable_name} = {value}")
                else:
                    results['warnings'].append(f"Target field {mapping.variable_name} not found")
                
            except Exception as e:
                results['failed_count'] += 1
                results['warnings'].append(f"Failed to apply mapping {mapping.variable_name}: {str(e)}")
        
        return results