# Path: repair_portal/patches/v15_04_workflow_state_normalization.py
# Date: 2025-01-21
# Version: 1.0.0
# Description: Comprehensive workflow state normalization patch to standardize Select field implementations and migrate data
# Dependencies: frappe, repair_portal module

import frappe
from frappe import _
import json

def execute():
    """
    Normalize workflow_state fields across all DocTypes:
    1. Fix Instrument Condition Record workflow states from Link to Select
    2. Migrate existing data to new format
    3. Ensure consistent workflow state values
    4. Add proper defaults for missing values
    """
    
    frappe.logger("migrations").info("Starting workflow state normalization patch v15.04")
    
    try:
        # 1. Fix Instrument Condition Record workflow states
        normalize_instrument_condition_record_workflow()
        
        # 2. Migrate existing workflow state data
        migrate_workflow_state_data()
        
        # 3. Add missing workflow states
        add_missing_workflow_states()
        
        # 4. Validate workflow state consistency
        validate_workflow_state_consistency()
        
        frappe.logger("migrations").info("Successfully completed workflow state normalization patch v15.04")
        
    except Exception as e:
        frappe.logger("migrations").error(f"Workflow state normalization patch failed: {str(e)}")
        frappe.log_error(f"Workflow State Normalization Error: {str(e)}", "Migration Patch v15.04")
        raise

def normalize_instrument_condition_record_workflow():
    """Fix Instrument Condition Record workflow_state field configuration"""
    
    if not frappe.db.table_exists("Instrument Condition Record"):
        frappe.logger("migrations").info("Instrument Condition Record table does not exist, skipping normalization")
        return
    
    frappe.logger("migrations").info("Normalizing Instrument Condition Record workflow states")
    
    # Map old Link-based values to new Select values
    old_to_new_mapping = {
        "Draft": "Draft",
        "Recorded": "Recorded", 
        "Verified": "Verified",
        "Archived": "Archived",
        # Handle any Link-based references that might exist
        "Workflow State": "Draft",  # Default fallback
        "": "Draft",  # Empty values default to Draft
        None: "Draft"  # NULL values default to Draft
    }
    
    # Get all records with workflow_state values
    if frappe.db.has_column("Instrument Condition Record", "workflow_state"):
        records = frappe.db.sql("""
            SELECT name, workflow_state 
            FROM `tabInstrument Condition Record` 
            WHERE workflow_state IS NOT NULL AND workflow_state != ''
        """, as_dict=True)
        
        updated_count = 0
        for record in records:
            old_value = record.get("workflow_state", "")
            new_value = old_to_new_mapping.get(old_value, "Draft")
            
            if old_value != new_value:
                frappe.db.set_value("Instrument Condition Record", record.name, "workflow_state", new_value)
                updated_count += 1
        
        frappe.logger("migrations").info(f"Updated {updated_count} Instrument Condition Record workflow states")
    
    # Set default workflow_state for records without one
    if frappe.db.has_column("Instrument Condition Record", "workflow_state"):
        frappe.db.sql("""
            UPDATE `tabInstrument Condition Record` 
            SET workflow_state = 'Draft' 
            WHERE workflow_state IS NULL OR workflow_state = ''
        """)
        
        default_count = frappe.db.sql("""
            SELECT COUNT(*) as count 
            FROM `tabInstrument Condition Record` 
            WHERE workflow_state = 'Draft'
        """)[0][0]
        
        frappe.logger("migrations").info(f"Set default workflow_state for {default_count} records")

def migrate_workflow_state_data():
    """Migrate workflow state data for all DocTypes with workflow_state fields"""
    
    frappe.logger("migrations").info("Migrating workflow state data across all DocTypes")
    
    # Instrument Profile workflow state migration
    if frappe.db.table_exists("Instrument Profile"):
        if frappe.db.has_column("Instrument Profile", "workflow_state"):
            # Ensure proper workflow state values
            valid_states = ["Open", "In Progress", "Delivered", "Archived"]
            
            # Get records with invalid workflow states
            invalid_records = frappe.db.sql("""
                SELECT name, workflow_state 
                FROM `tabInstrument Profile` 
                WHERE workflow_state NOT IN ('Open', 'In Progress', 'Delivered', 'Archived')
                   OR workflow_state IS NULL
            """, as_dict=True)
            
            for record in invalid_records:
                # Default to 'Open' for invalid states
                frappe.db.set_value("Instrument Profile", record.name, "workflow_state", "Open")
            
            frappe.logger("migrations").info(f"Fixed {len(invalid_records)} Instrument Profile workflow states")

def add_missing_workflow_states():
    """Add workflow_state values for records that don't have them"""
    
    frappe.logger("migrations").info("Adding missing workflow states")
    
    # Default workflow states for each DocType
    default_states = {
        "Instrument Profile": "Open",
        "Instrument Condition Record": "Draft",
        "Client Instrument Profile": "Draft",
        "Customer External Work Log": "Open"
    }
    
    for doctype, default_state in default_states.items():
        if frappe.db.table_exists(doctype) and frappe.db.has_column(doctype, "workflow_state"):
            # Update NULL or empty workflow states
            updated = frappe.db.sql(f"""
                UPDATE `tab{doctype}` 
                SET workflow_state = %s 
                WHERE workflow_state IS NULL OR workflow_state = ''
            """, (default_state,))
            
            count = frappe.db.sql(f"""
                SELECT COUNT(*) as count 
                FROM `tab{doctype}` 
                WHERE workflow_state = %s
            """, (default_state,))[0][0]
            
            frappe.logger("migrations").info(f"Set default workflow_state '{default_state}' for {count} {doctype} records")

def validate_workflow_state_consistency():
    """Validate that all workflow states are properly set and consistent"""
    
    frappe.logger("migrations").info("Validating workflow state consistency")
    
    validation_errors = []
    
    # Define expected workflow states for each DocType
    expected_states = {
        "Instrument Profile": ["Open", "In Progress", "Delivered", "Archived"],
        "Instrument Condition Record": ["Draft", "Recorded", "Verified", "Archived"],
        "Client Instrument Profile": ["Draft", "Active", "Archived"],
        "Customer External Work Log": ["Open", "In Progress", "Resolved", "Closed"]
    }
    
    for doctype, valid_states in expected_states.items():
        if frappe.db.table_exists(doctype) and frappe.db.has_column(doctype, "workflow_state"):
            # Check for invalid workflow states
            invalid_records = frappe.db.sql(f"""
                SELECT name, workflow_state 
                FROM `tab{doctype}` 
                WHERE workflow_state NOT IN ({','.join(['%s'] * len(valid_states))})
                   OR workflow_state IS NULL
            """, valid_states, as_dict=True)
            
            if invalid_records:
                validation_errors.append(f"{doctype}: {len(invalid_records)} records with invalid workflow states")
                
                # Fix invalid states by setting to first valid state
                default_state = valid_states[0]
                for record in invalid_records:
                    frappe.db.set_value(doctype, record.name, "workflow_state", default_state)
    
    if validation_errors:
        frappe.logger("migrations").warning(f"Fixed workflow state inconsistencies: {'; '.join(validation_errors)}")
    else:
        frappe.logger("migrations").info("All workflow states are consistent")
    
    # Final validation - ensure no NULL or empty workflow states remain
    for doctype in expected_states.keys():
        if frappe.db.table_exists(doctype) and frappe.db.has_column(doctype, "workflow_state"):
            null_count = frappe.db.sql(f"""
                SELECT COUNT(*) as count 
                FROM `tab{doctype}` 
                WHERE workflow_state IS NULL OR workflow_state = ''
            """)[0][0]
            
            if null_count > 0:
                frappe.logger("migrations").error(f"{doctype} still has {null_count} records with NULL/empty workflow_state")
            else:
                frappe.logger("migrations").info(f"{doctype} workflow states fully normalized")

    frappe.db.commit()
    frappe.logger("migrations").info("Workflow state validation completed successfully")