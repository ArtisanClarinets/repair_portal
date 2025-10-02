# Path: repair_portal/patches/v15_03_instrument_profile_indexes.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Add database indexes for instrument_profile module for query performance optimization
# Dependencies: frappe

import frappe


def execute():
    """
    Idempotent patch to add indexes on frequently queried fields in instrument_profile module.
    Safe to run multiple times.
    """
    indexes_to_add = [
        # Instrument Serial Number - most critical for lookups
        ('Instrument Serial Number', [
            ('serial', False),  # (fieldname, is_unique)
            ('normalized_serial', False),
            ('scan_code', False),
            ('instrument', False),
            ('verification_status', False),
            ('status', False),
        ]),
        
        # Instrument - frequent joins and filters
        ('Instrument', [
            ('serial_no', False),
            ('customer', False),
            ('brand', False),
            ('clarinet_type', False),
            ('instrument_category', False),
            ('current_status', False),
        ]),
        
        # Instrument Profile - main entity queries
        ('Instrument Profile', [
            ('instrument', False),
            ('customer', False),
            ('serial_no', False),
            ('workflow_state', False),
            ('status', False),
            ('warranty_end_date', False),
        ]),
        
        # Client Instrument Profile - customer portal queries
        ('Client Instrument Profile', [
            ('instrument_owner', False),
            ('verification_status', False),
            ('serial_no', False),
        ]),
        
        # Instrument Model - model lookups
        ('Instrument Model', [
            ('brand', False),
            ('instrument_category', False),
        ]),
        
        # Instrument Category - simple but frequently joined
        ('Instrument Category', [
            ('is_active', False),
        ]),
    ]
    
    for doctype, fields in indexes_to_add:
        if not frappe.db.table_exists(f'tab{doctype}'):
            frappe.log_error(f'Table tab{doctype} does not exist, skipping indexes', 'Patch: Instrument Profile Indexes')
            continue
        
        for fieldname, is_unique in fields:
            try:
                # Check if field exists in DocType
                if not frappe.get_meta(doctype).has_field(fieldname):
                    frappe.logger().info(f'Field {fieldname} does not exist in {doctype}, skipping index')
                    continue
                
                # Check if index already exists
                existing_indexes = frappe.db.sql(f"""
                    SELECT DISTINCT INDEX_NAME
                    FROM INFORMATION_SCHEMA.STATISTICS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = 'tab{doctype}'
                      AND COLUMN_NAME = '{fieldname}'
                """, as_dict=True)
                
                if existing_indexes:
                    frappe.logger().info(f'Index already exists on {doctype}.{fieldname}, skipping')
                    continue
                
                # Add index
                frappe.db.add_index(doctype, [fieldname])
                frappe.logger().info(f'✅ Added index on {doctype}.{fieldname}')
                
            except Exception as e:
                frappe.log_error(
                    f'Failed to add index on {doctype}.{fieldname}: {str(e)}',
                    'Patch: Instrument Profile Indexes'
                )
                # Non-fatal: continue with other indexes
                continue
    
    frappe.db.commit()
    frappe.logger().info('✅ Instrument Profile index patch completed')
