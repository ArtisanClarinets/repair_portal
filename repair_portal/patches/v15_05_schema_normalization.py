# Path: repair_portal/patches/v15_05_schema_normalization.py
# Date: 2025-01-21
# Version: 1.0.0
# Description: Comprehensive schema normalization patch for field consistency, data integrity, and constraint enforcement
# Dependencies: frappe, repair_portal module

import frappe
from frappe import _
import json

def execute():
    """
    Comprehensive schema normalization:
    1. Enforce field constraints and data types
    2. Normalize Select field options
    3. Clean up orphaned records
    4. Add missing required fields
    5. Validate Link field integrity
    """
    
    frappe.logger("migrations").info("Starting schema normalization patch v15.05")
    
    try:
        # 1. Normalize Select field options
        normalize_select_field_options()
        
        # 2. Clean up orphaned records and invalid links
        cleanup_orphaned_records()
        
        # 3. Enforce required field constraints
        enforce_required_fields()
        
        # 4. Validate and fix Link field integrity
        validate_link_field_integrity()
        
        # 5. Normalize date and datetime fields
        normalize_date_fields()
        
        # 6. Add missing audit fields
        add_missing_audit_fields()
        
        frappe.logger("migrations").info("Successfully completed schema normalization patch v15.05")
        
    except Exception as e:
        frappe.logger("migrations").error(f"Schema normalization patch failed: {str(e)}")
        frappe.log_error(f"Schema Normalization Error: {str(e)}", "Migration Patch v15.05")
        raise

def normalize_select_field_options():
    """Normalize Select field options across all DocTypes"""
    
    frappe.logger("migrations").info("Normalizing Select field options")
    
    # Instrument Profile status normalization
    if frappe.db.table_exists("Instrument Profile"):
        # Normalize status field values
        status_mapping = {
            "active": "Active",
            "inactive": "Inactive", 
            "maintenance": "Under Maintenance",
            "repair": "Under Repair",
            "retired": "Retired",
            "": "Active",  # Default for empty values
            None: "Active"  # Default for NULL values
        }
        
        if frappe.db.has_column("Instrument Profile", "status"):
            for old_value, new_value in status_mapping.items():
                # Handle NULL/empty defaults explicitly
                if old_value in ("", None):
                    if old_value == "":
                        where_clause = "(`status` IS NULL OR `status` = '')"
                    else:
                        where_clause = "(`status` IS NULL)"

                    frappe.db.sql(f"""
                        UPDATE `tabInstrument Profile`
                        SET `status` = %s
                        WHERE {where_clause}
                    """, (new_value,))
                else:
                    # Parameterized equality update for known old_value
                    frappe.db.sql(
                        """
                        UPDATE `tabInstrument Profile`
                        SET `status` = %s
                        WHERE `status` = %s
                        """,
                        (new_value, old_value),
                    )

            frappe.logger("migrations").info("Normalized Instrument Profile status field values")
    
    # Instrument Condition Record condition normalization
    if frappe.db.table_exists("Instrument Condition Record"):
        condition_mapping = {
            "new": "New",
            "good": "Good",
            "fair": "Fair", 
            "poor": "Poor",
            "needs repair": "Needs Repair",
            "needs_repair": "Needs Repair",
            "": "Fair",  # Default for empty values
            None: "Fair"  # Default for NULL values
        }
        
        if frappe.db.has_column("Instrument Condition Record", "condition"):
            for old_value, new_value in condition_mapping.items():
                # `condition` is a reserved word in some contexts; use backticks and parameterized queries
                if old_value in ("", None):
                    if old_value == "":
                        where_clause = "(`condition` IS NULL OR `condition` = '')"
                    else:
                        where_clause = "(`condition` IS NULL)"

                    frappe.db.sql(f"""
                        UPDATE `tabInstrument Condition Record`
                        SET `condition` = %s
                        WHERE {where_clause}
                    """, (new_value,))
                else:
                    frappe.db.sql(
                        """
                        UPDATE `tabInstrument Condition Record`
                        SET `condition` = %s
                        WHERE `condition` = %s
                        """,
                        (new_value, old_value),
                    )

            frappe.logger("migrations").info("Normalized Instrument Condition Record condition field values")

def cleanup_orphaned_records():
    """Clean up orphaned records and invalid Link references"""
    
    frappe.logger("migrations").info("Cleaning up orphaned records")
    
    # Clean up Instrument Condition Records with invalid instrument links
    if frappe.db.table_exists("Instrument Condition Record") and frappe.db.table_exists("Instrument"):
        orphaned_conditions = frappe.db.sql("""
            SELECT icr.name 
            FROM `tabInstrument Condition Record` icr
            LEFT JOIN `tabInstrument` i ON icr.instrument = i.name
            WHERE i.name IS NULL AND icr.instrument IS NOT NULL AND icr.instrument != ''
        """, as_dict=True)
        
        if orphaned_conditions:
            for record in orphaned_conditions:
                frappe.delete_doc("Instrument Condition Record", record.name, force=True)
            
            frappe.logger("migrations").info(f"Cleaned up {len(orphaned_conditions)} orphaned Instrument Condition Records")
    
    # Clean up Client Instrument Profiles with invalid customer links
    if frappe.db.table_exists("Client Instrument Profile") and frappe.db.table_exists("Customer"):
        orphaned_profiles = frappe.db.sql("""
            SELECT cip.name 
            FROM `tabClient Instrument Profile` cip
            LEFT JOIN `tabCustomer` c ON cip.customer = c.name
            WHERE c.name IS NULL AND cip.customer IS NOT NULL AND cip.customer != ''
        """, as_dict=True)
        
        if orphaned_profiles:
            for record in orphaned_profiles:
                frappe.delete_doc("Client Instrument Profile", record.name, force=True)
            
            frappe.logger("migrations").info(f"Cleaned up {len(orphaned_profiles)} orphaned Client Instrument Profiles")

def enforce_required_fields():
    """Enforce required field constraints by adding default values"""
    
    frappe.logger("migrations").info("Enforcing required field constraints")
    
    # Instrument Profile required fields
    if frappe.db.table_exists("Instrument Profile"):
        required_defaults = {
            "instrument_type": "Clarinet",
            "status": "Active",
            "current_location": "Shop",
            "condition": "Good"
        }
        
        for field, default_value in required_defaults.items():
            if frappe.db.has_column("Instrument Profile", field):
                # Use backticks around the column name to avoid reserved-word conflicts
                frappe.db.sql(f"""
                    UPDATE `tabInstrument Profile`
                    SET `{field}` = %s
                    WHERE `{field}` IS NULL OR `{field}` = ''
                """, (default_value,))

                count = frappe.db.sql(f"""
                    SELECT COUNT(*) as count
                    FROM `tabInstrument Profile`
                    WHERE `{field}` = %s
                """, (default_value,))[0][0]

                frappe.logger("migrations").info(f"Set default {field} = '{default_value}' for {count} Instrument Profile records")
    
    # Instrument Condition Record required fields
    if frappe.db.table_exists("Instrument Condition Record"):
        # Set date_of_record to creation date if missing
        if frappe.db.has_column("Instrument Condition Record", "date_of_record"):
            frappe.db.sql("""
                UPDATE `tabInstrument Condition Record` 
                SET date_of_record = DATE(creation) 
                WHERE date_of_record IS NULL
            """)
            
            # Set recorded_by to owner if missing
            frappe.db.sql("""
                UPDATE `tabInstrument Condition Record` 
                SET recorded_by = owner 
                WHERE recorded_by IS NULL OR recorded_by = ''
            """)
            
            frappe.logger("migrations").info("Set default date_of_record and recorded_by for Instrument Condition Records")

def validate_link_field_integrity():
    """Validate and fix Link field integrity"""
    
    frappe.logger("migrations").info("Validating Link field integrity")
    
    link_validations = [
        {
            "source_table": "Instrument Profile",
            "source_field": "customer",
            "target_table": "Customer",
            "action": "set_null"  # Set to NULL if customer doesn't exist
        },
        {
            "source_table": "Instrument Profile", 
            "source_field": "instrument_model",
            "target_table": "Instrument Model",
            "action": "set_default"  # Set to default model if doesn't exist
        },
        {
            "source_table": "Client Instrument Profile",
            "source_field": "instrument_profile",
            "target_table": "Instrument Profile",
            "action": "delete"  # Delete if instrument profile doesn't exist
        }
    ]
    
    for validation in link_validations:
        source_table = validation["source_table"]
        source_field = validation["source_field"]
        target_table = validation["target_table"]
        action = validation["action"]
        
        if not (frappe.db.table_exists(source_table) and frappe.db.table_exists(target_table)):
            continue
            
        if not frappe.db.has_column(source_table, source_field):
            continue

        # Find records with invalid links. We control table/field names in link_validations above.
        invalid_links = frappe.db.sql(f"""
            SELECT s.name, s.`{source_field}` as linked_value
            FROM `tab{source_table}` s
            LEFT JOIN `tab{target_table}` t ON s.`{source_field}` = t.name
            WHERE t.name IS NULL
              AND s.`{source_field}` IS NOT NULL
              AND s.`{source_field}` != ''
        """, as_dict=True)
        
        if invalid_links:
            if action == "set_null":
                for record in invalid_links:
                    # record.linked_value contains the original value from s.`{source_field}`
                    frappe.db.set_value(source_table, record.name, source_field, None)
                    
            elif action == "delete":
                for record in invalid_links:
                    frappe.delete_doc(source_table, record.name, force=True)
                    
            elif action == "set_default" and target_table == "Instrument Model":
                # Create a default instrument model if none exists
                default_model = frappe.db.get_value("Instrument Model", {"is_default": 1})
                if not default_model:
                    default_model = frappe.db.get_value("Instrument Model", {}, "name")
                
                if default_model:
                    for record in invalid_links:
                        frappe.db.set_value(source_table, record.name, source_field, default_model)
            
            frappe.logger("migrations").info(f"Fixed {len(invalid_links)} invalid {source_field} links in {source_table}")

def normalize_date_fields():
    """Normalize date and datetime fields"""
    
    frappe.logger("migrations").info("Normalizing date and datetime fields")
    
    # Set missing warranty_end_date to 1 year from creation
    if frappe.db.table_exists("Instrument Profile"):
        if frappe.db.has_column("Instrument Profile", "warranty_end_date"):
            frappe.db.sql("""
                UPDATE `tabInstrument Profile` 
                SET warranty_end_date = DATE_ADD(DATE(creation), INTERVAL 1 YEAR)
                WHERE warranty_end_date IS NULL
            """)
            
            frappe.logger("migrations").info("Set default warranty_end_date for Instrument Profiles")
    
    # Set missing last_service_date to creation date
    if frappe.db.table_exists("Instrument Profile"):
        if frappe.db.has_column("Instrument Profile", "last_service_date"):
            frappe.db.sql("""
                UPDATE `tabInstrument Profile` 
                SET last_service_date = DATE(creation)
                WHERE last_service_date IS NULL
            """)
            
            frappe.logger("migrations").info("Set default last_service_date for Instrument Profiles")

def add_missing_audit_fields():
    """Add missing audit and tracking fields"""
    
    frappe.logger("migrations").info("Adding missing audit fields")
    
    # Ensure all records have proper owner and creation timestamps
    audit_tables = ["Instrument Profile", "Instrument Condition Record", "Client Instrument Profile"]
    
    for table in audit_tables:
        if frappe.db.table_exists(table):
            # Set missing owner to Administrator
            if frappe.db.has_column(table, "owner"):
                frappe.db.sql(f"""
                    UPDATE `tab{table}` 
                    SET owner = 'Administrator' 
                    WHERE owner IS NULL OR owner = ''
                """)
            
            # Set missing modified_by to owner
            if frappe.db.has_column(table, "modified_by"):
                frappe.db.sql(f"""
                    UPDATE `tab{table}` 
                    SET modified_by = owner 
                    WHERE modified_by IS NULL OR modified_by = ''
                """)
            
            frappe.logger("migrations").info(f"Set missing audit fields for {table}")
    
    frappe.db.commit()
    frappe.logger("migrations").info("Schema normalization completed successfully")