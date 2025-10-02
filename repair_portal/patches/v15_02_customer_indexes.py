# Path: repair_portal/repair_portal/patches/v15_02_customer_indexes.py
# Date: 2025-01-27
# Version: 1.0.0
# Description: Add database indexes for customer module performance optimization
# Dependencies: frappe

import frappe


def execute():
    """Add performance indexes for customer module DocTypes."""
    
    # Customer DocType indexes
    if frappe.db.table_exists("tabCustomer"):
        _add_index_safely("tabCustomer", "workflow_state")
        _add_index_safely("tabCustomer", "customer_type")
        _add_index_safely("tabCustomer", "creation")
        _add_index_safely("tabCustomer", "modified")
        
    # Consent Form indexes
    if frappe.db.table_exists("tabConsent Form"):
        _add_index_safely("tabConsent Form", "customer")
        _add_index_safely("tabConsent Form", "consent_template")
        _add_index_safely("tabConsent Form", "status")
        _add_index_safely("tabConsent Form", "signed_on")
        _add_index_safely("tabConsent Form", "docstatus")
        _add_index_safely("tabConsent Form", ["customer", "status"])
        _add_index_safely("tabConsent Form", ["consent_template", "docstatus"])
    
    # Consent Template indexes
    if frappe.db.table_exists("tabConsent Template"):
        _add_index_safely("tabConsent Template", "disabled")
        _add_index_safely("tabConsent Template", "status")
        _add_index_safely("tabConsent Template", "last_modified_on")
        
    # Consent Log Entry indexes
    if frappe.db.table_exists("tabConsent Log Entry"):
        _add_index_safely("tabConsent Log Entry", "parent")
        _add_index_safely("tabConsent Log Entry", "status")
        _add_index_safely("tabConsent Log Entry", "entry_date")
        _add_index_safely("tabConsent Log Entry", "method")
        _add_index_safely("tabConsent Log Entry", "expires_on")
        _add_index_safely("tabConsent Log Entry", ["parent", "status"])
        _add_index_safely("tabConsent Log Entry", ["status", "expires_on"])
        
    # Consent Field Value indexes
    if frappe.db.table_exists("tabConsent Field Value"):
        _add_index_safely("tabConsent Field Value", "parent")
        _add_index_safely("tabConsent Field Value", "field_label")
        _add_index_safely("tabConsent Field Value", "field_type")
        _add_index_safely("tabConsent Field Value", ["parent", "field_label"])
        
    # Customer Type indexes
    if frappe.db.table_exists("tabCustomer Type"):
        _add_index_safely("tabCustomer Type", "is_default")
        _add_index_safely("tabCustomer Type", "disabled")
        
    # Instruments Owned indexes
    if frappe.db.table_exists("tabInstruments Owned"):
        _add_index_safely("tabInstruments Owned", "parent")
        _add_index_safely("tabInstruments Owned", "instrument_profile")
        _add_index_safely("tabInstruments Owned", "serial_no")
        _add_index_safely("tabInstruments Owned", "ownership_status")
        _add_index_safely("tabInstruments Owned", "warranty_status")
        _add_index_safely("tabInstruments Owned", ["parent", "ownership_status"])
        _add_index_safely("tabInstruments Owned", ["serial_no", "ownership_status"])
        
    # Linked Players indexes
    if frappe.db.table_exists("tabLinked Players"):
        _add_index_safely("tabLinked Players", "parent")
        _add_index_safely("tabLinked Players", "player_profile")
        _add_index_safely("tabLinked Players", "person")
        _add_index_safely("tabLinked Players", "is_primary")
        _add_index_safely("tabLinked Players", "relationship")
        _add_index_safely("tabLinked Players", ["parent", "is_primary"])
        _add_index_safely("tabLinked Players", ["player_profile", "parent"])
        
    # Performance optimization for large tables
    _optimize_table_performance()
    
    frappe.db.commit()
    print("Successfully added customer module performance indexes")


def _add_index_safely(table: str, columns):
    """Add index safely, checking if it already exists."""
    try:
        if isinstance(columns, str):
            index_name = f"idx_{table}_{columns}"
            columns_str = columns
        else:
            # Multiple columns
            index_name = f"idx_{table}_{'_'.join(columns)}"
            columns_str = ", ".join(columns)
        
        # Check if index already exists
        existing_indexes = frappe.db.sql(f"""
            SHOW INDEX FROM `{table}` 
            WHERE Key_name = '{index_name}'
        """)
        
        if not existing_indexes:
            frappe.db.sql(f"""
                ALTER TABLE `{table}` 
                ADD INDEX `{index_name}` ({columns_str})
            """)
            print(f"Added index {index_name} to {table}")
        else:
            print(f"Index {index_name} already exists on {table}")
            
    except Exception as e:
        print(f"Failed to add index to {table}.{columns}: {str(e)}")
        # Don't fail the entire patch for individual index failures


def _optimize_table_performance():
    """Apply performance optimizations to tables."""
    try:
        # Analyze tables for better query optimization
        tables_to_analyze = [
            "tabCustomer",
            "tabConsent Form", 
            "tabConsent Log Entry",
            "tabConsent Field Value",
            "tabInstruments Owned",
            "tabLinked Players"
        ]
        
        for table in tables_to_analyze:
            if frappe.db.table_exists(table):
                try:
                    frappe.db.sql(f"ANALYZE TABLE `{table}`")
                    print(f"Analyzed table {table}")
                except Exception as e:
                    print(f"Failed to analyze {table}: {str(e)}")
                    
    except Exception as e:
        print(f"Table optimization failed: {str(e)}")