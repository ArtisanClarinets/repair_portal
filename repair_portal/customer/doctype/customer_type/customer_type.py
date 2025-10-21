# Path: repair_portal/repair_portal/customer/doctype/customer_type/customer_type.py
# Date: 2025-01-27
# Version: 2.0.0
# Description: Customer Type DocType with single-default enforcement, validation, and utility methods
# Dependencies: frappe.model.document, frappe.db

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint


class CustomerType(Document):
    """
    Customer Type master with single-default enforcement and validation.

    Manages customer categorization with automatic default handling,
    validation rules, and utility methods for customer assignment.
    """

    def validate(self) -> None:
        """Validate customer type configuration"""
        self._validate_required_fields()
        self._validate_unique_name()
        self._deduplicate_default()
        self._validate_customer_usage()

    def before_save(self) -> None:
        """Pre-save operations"""
        self._ensure_single_default()
        self._update_audit_fields()

    def on_update(self) -> None:
        """Post-update operations"""
        self._update_linked_customers()
        self._log_changes()

    def before_delete(self) -> None:
        """Pre-delete validation"""
        self._validate_deletion_allowed()

    def _validate_required_fields(self) -> None:
        """Validate required fields"""
        if not self.type_name:
            frappe.throw(_("Type Name is required"))

    def _validate_unique_name(self) -> None:
        """Validate name uniqueness"""
        if self.is_new():
            existing = frappe.db.exists(
                "Customer Type", {"type_name": self.type_name, "name": ["!=", self.name]}
            )
            if existing:
                frappe.throw(_("Customer Type with name '{0}' already exists").format(self.type_name))

    def _deduplicate_default(self) -> None:
        """Ensure only one customer type is marked as default"""
        if not cint(self.is_default):
            return

        try:
            # Clear default from other customer types
            frappe.db.sql(
                """
                UPDATE `tabCustomer Type`
                SET is_default = 0
                WHERE name != %s AND is_default = 1
            """,
                (self.name,),
            )

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "CustomerType: deduplication failed")
            frappe.throw(_("Failed to update default customer type: {0}").format(str(e)))

    def _ensure_single_default(self) -> None:
        """Ensure there's always one default if this is the only type"""
        if not cint(self.is_default):
            # If no other defaults exist, make this one default
            existing_defaults = frappe.db.count("Customer Type", {"is_default": 1})
            if existing_defaults == 0:
                self.is_default = 1

    def _validate_customer_usage(self) -> None:
        """Validate if customer type is in use when changing key properties"""
        if not self.is_new():
            # Check if customers are using this type
            customer_count = frappe.db.count("Customer", {"customer_type": self.name})
            if customer_count > 0:
                # Allow updates but warn about impact
                if self.has_value_changed("disabled") and self.disabled:
                    frappe.msgprint(
                        _(
                            "Warning: {0} customers are using this customer type. "
                            "Disabling it may affect their access."
                        ).format(customer_count),
                        alert=True,
                    )

    def _validate_deletion_allowed(self) -> None:
        """Validate if customer type can be deleted"""
        # Check if customers are using this type
        customers_using = frappe.db.get_list(
            "Customer", filters={"customer_type": self.name}, fields=["name", "customer_name"], limit=5
        )

        if customers_using:
            customer_names = [f"'{c.customer_name}'" for c in customers_using[:3]]
            if len(customers_using) > 3:
                customer_names.append(f"and {len(customers_using) - 3} more")

            frappe.throw(
                _("Cannot delete Customer Type. It is being used by customers: {0}").format(
                    ", ".join(customer_names)
                )
            )

        # Don't allow deleting the last customer type
        total_types = frappe.db.count("Customer Type", {"disabled": 0})
        if total_types <= 1:
            frappe.throw(_("Cannot delete the last active Customer Type"))

    def _update_audit_fields(self) -> None:
        """Update audit fields"""
        if self.is_new():
            self.created_by = frappe.session.user
            self.creation_date = frappe.utils.now()
        else:
            self.modified_by = frappe.session.user
            self.modified_date = frappe.utils.now()

    def _update_linked_customers(self) -> None:
        """Update linked customers if customer type label changed"""
        if self.has_value_changed("type_name"):
            # This would typically trigger cache updates
            frappe.cache().delete_keys("customer_type_*")

    def _log_changes(self) -> None:
        """Log significant changes"""
        if self.has_value_changed("is_default") and self.is_default:
            frappe.logger().info(f"Customer Type '{self.name}' set as default")

        if self.has_value_changed("disabled") and self.disabled:
            frappe.logger().info(f"Customer Type '{self.name}' disabled")

    @frappe.whitelist()
    def get_customer_count(self) -> int:
        """Get count of customers using this type"""
        return frappe.db.count("Customer", {"customer_type": self.name})

    @frappe.whitelist()
    def get_customer_list(self, limit: int = 50) -> list[dict]:
        """Get list of customers using this type"""
        return frappe.db.get_list(
            "Customer",
            filters={"customer_type": self.name},
            fields=["name", "customer_name", "customer_group", "creation"],
            order_by="creation desc",
            limit=limit,
        )

    @staticmethod
    @frappe.whitelist()
    def get_default_customer_type() -> str | None:
        """Get the default customer type"""
        default_type = frappe.db.get_value("Customer Type", {"is_default": 1, "disabled": 0}, "name")

        if not default_type:
            # If no default set, get the first active one
            default_type = frappe.db.get_value("Customer Type", {"disabled": 0}, "name", order_by="creation")

        return default_type

    @staticmethod
    @frappe.whitelist()
    def get_active_customer_types() -> list[dict]:
        """Get list of active customer types"""
        return frappe.db.get_list(
            "Customer Type",
            filters={"disabled": 0},
            fields=["name", "type_name", "description", "is_default"],
            order_by="is_default desc, type_name"
        )
