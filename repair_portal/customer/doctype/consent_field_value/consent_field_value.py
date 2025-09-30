# Path: repair_portal/repair_portal/customer/doctype/consent_field_value/consent_field_value.py
# Date: 2025-01-27
# Version: 2.0.0
# Description: Child table for storing consent form field values with validation and type coercion
# Dependencies: frappe.model.document, typing

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate


class ConsentFieldValue(Document):
    """
    Child table for storing consent form field values.
    
    Stores field label, type, and entered value for each filled consent.
    Provides validation and type coercion for different field types.
    """
    
    def validate(self) -> None:
        """Validate field value based on field type"""
        self._validate_required_fields()
        self._validate_field_value()
        self._coerce_field_value()
    
    def _validate_required_fields(self) -> None:
        """Validate required fields"""
        if not self.field_label:
            frappe.throw(_("Field Label is required"))
        
        if not self.field_type:
            frappe.throw(_("Field Type is required"))
    
    def _validate_field_value(self) -> None:
        """Validate field value based on type"""
        if not self.field_value:
            return
        
        try:
            if self.field_type == "Int":
                cint(self.field_value)
            elif self.field_type == "Float":
                flt(self.field_value)
            elif self.field_type == "Date":
                getdate(self.field_value)
            elif self.field_type == "Check":
                if self.field_value not in ["0", "1", "true", "false"]:
                    frappe.throw(_("Check field must be 0, 1, true, or false"))
        except Exception:
            frappe.throw(_("Invalid value for field type {0}").format(self.field_type))
    
    def _coerce_field_value(self) -> None:
        """Coerce field value to appropriate type"""
        if not self.field_value:
            return
        
        try:
            if self.field_type == "Int":
                self.field_value = str(cint(self.field_value))
            elif self.field_type == "Float":
                self.field_value = str(flt(self.field_value))
            elif self.field_type == "Check":
                self.field_value = "1" if self.field_value in ["1", "true", True] else "0"
        except Exception:
            pass  # Keep original value if coercion fails
    
    def get_typed_value(self) -> Any:
        """Return properly typed value for programmatic use"""
        if not self.field_value:
            return None
        
        try:
            if self.field_type == "Int":
                return cint(self.field_value)
            elif self.field_type == "Float":
                return flt(self.field_value)
            elif self.field_type == "Date":
                return getdate(self.field_value)
            elif self.field_type == "Check":
                return bool(cint(self.field_value))
            else:
                return self.field_value
        except Exception:
            return self.field_value
