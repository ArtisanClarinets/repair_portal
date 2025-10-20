# Path: repair_portal/repair_logging/patches/v15_01_add_performance_indexes.py
# Date: 2025-01-14
# Version: 1.0.0
# Description: Add performance indexes for repair_logging module tables
# Dependencies: frappe

import frappe


def execute():
    """Add performance indexes for repair_logging tables."""

    indexes_to_add = [
        # Material Use Log indexes
        ("Material Use Log", ["material_name"]),
        ("Material Use Log", ["technician"]),
        ("Material Use Log", ["operation_type", "operation_link"]),
        ("Material Use Log", ["creation"]),
        # Repair Task Log indexes
        ("Repair Task Log", ["status"]),
        ("Repair Task Log", ["technician"]),
        ("Repair Task Log", ["priority"]),
        ("Repair Task Log", ["start_time"]),
        # Instrument Interaction Log indexes
        ("Instrument Interaction Log", ["instrument_reference"]),
        ("Instrument Interaction Log", ["interaction_type"]),
        ("Instrument Interaction Log", ["technician"]),
        ("Instrument Interaction Log", ["creation"]),
        # Key Measurement indexes
        ("Key Measurement", ["instrument_reference"]),
        ("Key Measurement", ["measurement_name"]),
        ("Key Measurement", ["technician"]),
        # Visual Inspection indexes
        ("Visual Inspection", ["instrument_reference"]),
        ("Visual Inspection", ["inspection_type"]),
        ("Visual Inspection", ["inspector"]),
        ("Visual Inspection", ["overall_condition_rating"]),
        # Tool Usage Log indexes
        ("Tool Usage Log", ["tool_name"]),
        ("Tool Usage Log", ["technician"]),
        ("Tool Usage Log", ["operation_type", "operation_link"]),
        # Warranty Modification Log indexes
        ("Warranty Modification Log", ["instrument_reference"]),
        ("Warranty Modification Log", ["modification_type"]),
        ("Warranty Modification Log", ["technician"]),
        # Diagnostic Metrics indexes
        ("Diagnostic Metrics", ["instrument_reference"]),
        ("Diagnostic Metrics", ["metric_type"]),
        ("Diagnostic Metrics", ["technician"]),
        # Tenon Measurement indexes
        ("Tenon Measurement", ["instrument_reference"]),
        ("Tenon Measurement", ["joint_position"]),
        ("Tenon Measurement", ["technician"]),
        # Tone Hole Inspection indexes
        ("Tone Hole Inspection Record", ["instrument_reference"]),
        ("Tone Hole Inspection Record", ["hole_number"]),
        ("Tone Hole Inspection Record", ["inspector"]),
        # Pad Condition indexes
        ("Pad Condition", ["instrument_reference"]),
        ("Pad Condition", ["pad_position"]),
        ("Pad Condition", ["overall_condition_rating"]),
        # Related Instrument Interaction indexes
        ("Related Instrument Interaction", ["primary_instrument"]),
        ("Related Instrument Interaction", ["related_instrument"]),
        ("Related Instrument Interaction", ["interaction_type"]),
    ]

    for table_name, columns in indexes_to_add:
        try:
            if frappe.db.table_exists(table_name):
                # Check if index already exists
                index_name = f"idx_{table_name.lower().replace(' ', '_')}_{'_'.join(columns)}"

                # Create index if it doesn't exist
                existing_indexes = frappe.db.sql(
                    f"""
                    SHOW INDEX FROM `tab{table_name}` 
                    WHERE Key_name = %s
                """,
                    (index_name,),
                )

                if not existing_indexes:
                    column_list = ", ".join([f"`{col}`" for col in columns])
                    frappe.db.sql(
                        f"""
                        CREATE INDEX `{index_name}` 
                        ON `tab{table_name}` ({column_list})
                    """
                    )
                    frappe.logger().info(f"Created index {index_name} on {table_name}")
                else:
                    frappe.logger().info(f"Index {index_name} already exists on {table_name}")

        except Exception as e:
            frappe.logger().error(f"Failed to create index on {table_name}: {str(e)}")
            # Don't fail the patch for index issues
            continue

    frappe.logger().info("Performance indexes creation completed for repair_logging module")
