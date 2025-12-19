import frappe

def execute():
    """Add core performance indexes for high-traffic tables."""

    # List of (Table, IndexName, Columns)
    # Columns string can include DESC
    indexes = [
        ("Instrument Profile", "idx_customer_status", "customer, profile_status"),
        ("Instrument Profile", "idx_creation_desc", "creation DESC"),
        ("Repair Order", "idx_workflow_state", "workflow_state"),
        ("Repair Order", "idx_customer_modified", "customer, modified DESC"),
        ("Clarinet Intake", "idx_workflow_customer", "workflow_state, customer"),
        ("Repair Log", "idx_customer_date", "customer, creation DESC"),
        ("Player Profile", "idx_customer_published", "customer, published"),
    ]

    for doctype, index_name, columns in indexes:
        if not frappe.db.table_exists(doctype):
            continue

        table = f"tab{doctype}"
        try:
            # Check if index exists
            exists = frappe.db.sql(f"SHOW INDEX FROM `{table}` WHERE Key_name = %s", (index_name,))
            if not exists:
                frappe.db.sql(f"ALTER TABLE `{table}` ADD INDEX `{index_name}` ({columns})")
                frappe.logger().info(f"Added index {index_name} to {doctype}")
        except Exception as e:
            frappe.logger().error(f"Failed to add index {index_name} to {doctype}: {e}")
