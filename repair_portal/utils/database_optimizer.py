# Database Query Performance Optimization Guide
# Last Updated: 2025-07-19
# Version: v1.0
# Purpose: Best practices for high-performance database queries in repair_portal

from typing import Any

import frappe
from frappe.utils import add_days, cint, getdate


class DatabaseOptimizer:
    """
    Enterprise-grade database query optimization patterns for repair_portal.
    Implements Fortune-500 level performance standards.
    """

    @staticmethod
    def get_optimized_instrument_list(filters: dict | None = None, limit: int = 50) -> list[dict[str, Any]]:
        """
        Optimized instrument profile queries with proper indexing and filtering.

        Performance Improvements:
        - Uses indexed fields for WHERE clauses
        - Limits result set size
        - Selective field fetching
        - Proper parameter binding
        """
        filters = filters or {}

        # Build conditions with proper indexing
        conditions = []
        params = {}

        if filters.get("customer"):
            conditions.append("customer = %(customer)s")
            params["customer"] = filters["customer"]

        if filters.get("status"):
            conditions.append("profile_status = %(status)s")
            params["status"] = filters["status"]

        if filters.get("instrument_category"):
            conditions.append("instrument_category = %(category)s")
            params["category"] = filters["instrument_category"]

        # Date range filtering with indexed creation field
        if filters.get("from_date"):
            conditions.append("creation >= %(from_date)s")
            params["from_date"] = getdate(filters["from_date"])

        if filters.get("to_date"):
            conditions.append("creation <= %(to_date)s")
            params["to_date"] = getdate(filters["to_date"])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        result = frappe.db.sql(
            f"""
            SELECT 
                name,
                serial_no,
                instrument_category,
                brand,
                model,
                profile_status,
                customer,
                modified
            FROM `tabInstrument Profile`
            {where_clause}
            ORDER BY modified DESC
            LIMIT {cint(limit)}
        """,
            params,
            as_dict=True,
        )
        # Ensure result is always a list of dicts
        if isinstance(result, list):
            # Filter out any non-dict items for type safety
            return [row for row in result if isinstance(row, dict)]
        return [row for row in list(result) if isinstance(row, dict)] if result else []

    @staticmethod
    def get_repair_dashboard_metrics(user: str | None = None) -> dict[str, Any]:
        """
        High-performance dashboard metrics with single-query aggregation.

        Performance Improvements:
        - Single query with CASE statements for multiple counts
        - Uses indexed workflow_state field
        - Role-based filtering
        """
        user = user or frappe.session.user

        # Check if user has full access or needs filtering
        roles = frappe.get_roles(user)
        user_filter = ""
        params = {}

        if "System Manager" not in roles and "Repair Manager" not in roles:
            if "Technician" in roles:
                user_filter = "AND technician = %(user)s"
                params["user"] = user
            else:
                # Customer access - filter by their instruments
                customer = frappe.db.get_value("Customer", {"linked_user": user}, "name")
                if customer:
                    user_filter = "AND customer = %(customer)s"
                    params["customer"] = customer
                else:
                    return {}  # No access

        result = frappe.db.sql(
            f"""
            SELECT
                COUNT(*) AS total_repairs,
                SUM(CASE WHEN workflow_state = 'Draft' THEN 1 ELSE 0 END) AS draft_count,
                SUM(CASE WHEN workflow_state = 'In Progress' THEN 1 ELSE 0 END) AS in_progress_count,
                SUM(CASE WHEN workflow_state = 'QA' THEN 1 ELSE 0 END) AS qa_count,
                SUM(CASE WHEN workflow_state = 'Completed' THEN 1 ELSE 0 END) AS completed_count,
                AVG(CASE WHEN workflow_state = 'Completed' AND estimated_hours > 0 
                    THEN actual_hours / estimated_hours ELSE NULL END) AS efficiency_ratio
            FROM `tabRepair Order`
            WHERE docstatus != 2 {user_filter}
        """,
            params,
            as_dict=True,
        )
        # Ensure result is a list and return first dict or empty dict
        result_list = list(result) if result else []
        return result_list[0] if result_list and isinstance(result_list[0], dict) else {}

    @staticmethod
    def bulk_update_workflow_states(updates: list[dict[str, str]], doctype: str = "Repair Order") -> int:
        """
        Optimized bulk updates for workflow state changes.

        Performance Improvements:
        - Single transaction for all updates
        - Batch processing
        - Proper error handling with rollback
        """
        if not updates:
            return 0

        try:
            # Use explicit transaction for atomic updates
            frappe.db.begin()

            update_count = 0
            for update in updates:
                if update.get("name") and update.get("workflow_state"):
                    frappe.db.set_value(
                        doctype,
                        update["name"],
                        "workflow_state",
                        update["workflow_state"],
                        update_modified=True,
                    )
                    update_count += 1

            frappe.db.commit()
            return update_count

        except Exception as e:
            frappe.db.rollback()
            frappe.log_error(f"Bulk workflow update failed: {str(e)}")
            raise

    @staticmethod
    def get_cached_customer_instruments(customer: str, cache_ttl: int = 300) -> list[dict]:
        """
        Cached customer instrument lookup with TTL.

        Performance Improvements:
        - Redis caching with TTL
        - Reduced database hits for frequent queries
        - Automatic cache invalidation
        """
        cache_key = f"customer_instruments:{customer}"

        # Try to get from cache first
        cached_data = frappe.cache().get_value(cache_key)
        if cached_data:
            return cached_data

        # Fetch from database if not cached
        instruments = frappe.get_all(
            "Instrument Profile",
            filters={"customer": customer, "profile_status": ["!=", "Archived"]},
            fields=["name", "serial_no", "instrument_category", "brand", "model", "profile_status"],
            order_by="modified desc",
        )

        # Cache the result
        frappe.cache().set_value(cache_key, instruments, expires_in_sec=cache_ttl)

        return instruments

    @staticmethod
    def invalidate_customer_cache(customer: str):
        """Invalidate customer-related cache entries."""
        cache_keys = [
            f"customer_instruments:{customer}",
            f"customer_repairs:{customer}",
            f"customer_metrics:{customer}",
        ]

        for key in cache_keys:
            frappe.cache().delete_value(key)


# Example usage in API endpoints:
@frappe.whitelist(allow_guest=False)
def get_optimized_dashboard_data():
    """Example of optimized API endpoint using the DatabaseOptimizer."""
    try:
        # Get user-specific metrics with single query
        metrics = DatabaseOptimizer.get_repair_dashboard_metrics()

        # Get recent instruments with pagination and filtering
        recent_instruments = DatabaseOptimizer.get_optimized_instrument_list(
            filters={"from_date": add_days(getdate(), -30)}, limit=20
        )

        return {"success": True, "metrics": metrics, "recent_instruments": recent_instruments}

    except Exception as e:
        frappe.log_error(f"Dashboard data fetch failed: {str(e)}")
        return {"success": False, "error": "Failed to fetch dashboard data"}


# Database indexing recommendations:
RECOMMENDED_INDEXES = [
    # High-traffic query indexes
    "ALTER TABLE `tabInstrument Profile` ADD INDEX idx_customer_status (customer, profile_status);",
    "ALTER TABLE `tabInstrument Profile` ADD INDEX idx_creation_desc (creation DESC);",
    "ALTER TABLE `tabRepair Order` ADD INDEX idx_workflow_state (workflow_state);",
    "ALTER TABLE `tabRepair Order` ADD INDEX idx_customer_modified (customer, modified DESC);",
    "ALTER TABLE `tabClarinet Intake` ADD INDEX idx_workflow_customer (workflow_state, customer);",
    # Performance-critical composite indexes
    "ALTER TABLE `tabRepair Log` ADD INDEX idx_customer_date (customer, creation DESC);",
    "ALTER TABLE `tabPlayer Profile` ADD INDEX idx_customer_published (customer, published);",
    "ALTER TABLE `tabSerial No` ADD INDEX idx_status_warehouse (status, warehouse);",
]
