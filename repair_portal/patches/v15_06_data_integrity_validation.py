# Path: repair_portal/patches/v15_06_data_integrity_validation.py
# Date: 2025-01-21
# Version: 1.0.0
# Description: Comprehensive data integrity validation and constraint enforcement patch
# Dependencies: frappe, repair_portal module

import frappe
from frappe import _

def execute():
    """
    Comprehensive data integrity validation:
    1. Validate unique constraints
    2. Enforce referential integrity
    3. Add database constraints
    4. Validate business rules
    5. Generate integrity report
    """
    
    frappe.logger("migrations").info("Starting data integrity validation patch v15.06")
    
    try:
        # 1. Validate and fix unique constraints
        validate_unique_constraints()
        
        # 2. Enforce referential integrity
        enforce_referential_integrity()
        
        # 3. Validate business rules
        validate_business_rules()
        
        # 4. Add database constraints
        add_database_constraints()
        
        # 5. Generate integrity report
        generate_integrity_report()
        
        frappe.logger("migrations").info("Successfully completed data integrity validation patch v15.06")
        
    except Exception as e:
        frappe.logger("migrations").error(f"Data integrity validation patch failed: {str(e)}")
        frappe.log_error(f"Data Integrity Validation Error: {str(e)}", "Migration Patch v15.06")
        raise

def validate_unique_constraints():
    """Validate and fix unique constraint violations"""
    
    frappe.logger("migrations").info("Validating unique constraints")
    
    # Check for duplicate Instrument serial numbers
    if frappe.db.table_exists("Instrument"):
        if frappe.db.has_column("Instrument", "serial_no"):
            duplicates = frappe.db.sql("""
                SELECT serial_no, COUNT(*) as count
                FROM `tabInstrument`
                WHERE serial_no IS NOT NULL AND serial_no != ''
                GROUP BY serial_no
                HAVING COUNT(*) > 1
            """, as_dict=True)
            
            if duplicates:
                for dup in duplicates:
                    # Get all records with this serial number
                    records = frappe.db.sql("""
                        SELECT name, creation
                        FROM `tabInstrument`
                        WHERE serial_no = %s
                        ORDER BY creation
                    """, (dup.serial_no,), as_dict=True)
                    
                    # Keep the oldest record, rename others
                    for i, record in enumerate(records[1:], 1):
                        new_serial = f"{dup.serial_no}-DUP-{i}"
                        frappe.db.set_value("Instrument", record.name, "serial_no", new_serial)
                
                frappe.logger("migrations").info(f"Fixed {len(duplicates)} duplicate Instrument serial numbers")
    
    # Check for duplicate Instrument Profile names
    if frappe.db.table_exists("Instrument Profile"):
        duplicates = frappe.db.sql("""
            SELECT name, COUNT(*) as count
            FROM `tabInstrument Profile`
            GROUP BY name
            HAVING COUNT(*) > 1
        """, as_dict=True)
        
        if duplicates:
            frappe.logger("migrations").warning(f"Found {len(duplicates)} duplicate Instrument Profile names")

def enforce_referential_integrity():
    """Enforce referential integrity across related tables"""
    
    frappe.logger("migrations").info("Enforcing referential integrity")
    
    # Validate Instrument Profile -> Customer relationships
    if frappe.db.table_exists("Instrument Profile") and frappe.db.table_exists("Customer"):
        invalid_customers = frappe.db.sql("""
            SELECT ip.name, ip.customer
            FROM `tabInstrument Profile` ip
            LEFT JOIN `tabCustomer` c ON ip.customer = c.name
            WHERE ip.customer IS NOT NULL 
              AND ip.customer != ''
              AND c.name IS NULL
        """, as_dict=True)
        
        if invalid_customers:
            for record in invalid_customers:
                frappe.db.set_value("Instrument Profile", record.name, "customer", None)
            
            frappe.logger("migrations").info(f"Cleared {len(invalid_customers)} invalid customer references")
    
    # Validate Instrument Profile -> Instrument Model relationships
    if frappe.db.table_exists("Instrument Profile") and frappe.db.table_exists("Instrument Model"):
        # Ensure the Instrument Profile actually has the instrument_model column before querying it
        if frappe.db.has_column("Instrument Profile", "instrument_model") and frappe.db.has_column("Instrument Model", "name"):
            invalid_models = frappe.db.sql("""
                SELECT ip.name, ip.instrument_model
                FROM `tabInstrument Profile` ip
                LEFT JOIN `tabInstrument Model` im ON ip.instrument_model = im.name
                WHERE ip.instrument_model IS NOT NULL
                  AND ip.instrument_model != ''
                  AND im.name IS NULL
            """, as_dict=True)
        else:
            invalid_models = []
        
        if invalid_models:
            # Get a default instrument model
            default_model = frappe.db.get_value("Instrument Model", {}, "name")
            if default_model:
                for record in invalid_models:
                    frappe.db.set_value("Instrument Profile", record.name, "instrument_model", default_model)
            else:
                for record in invalid_models:
                    frappe.db.set_value("Instrument Profile", record.name, "instrument_model", None)
            
            frappe.logger("migrations").info(f"Fixed {len(invalid_models)} invalid instrument model references")

def validate_business_rules():
    """Validate business rules and constraints"""
    
    frappe.logger("migrations").info("Validating business rules")
    
    # Validate warranty dates
    if frappe.db.table_exists("Instrument Profile"):
        if frappe.db.has_column("Instrument Profile", "warranty_end_date"):
            # Fix warranty end dates that are before start dates
            invalid_warranties = frappe.db.sql("""
                UPDATE `tabInstrument Profile`
                SET warranty_end_date = DATE_ADD(DATE(creation), INTERVAL 1 YEAR)
                WHERE warranty_end_date < DATE(creation)
            """)
            
            frappe.logger("migrations").info("Fixed invalid warranty end dates")
    
    # Validate condition dates
    if frappe.db.table_exists("Instrument Condition Record"):
        if frappe.db.has_column("Instrument Condition Record", "date_of_record"):
            # Fix future condition record dates
            future_dates = frappe.db.sql("""
                UPDATE `tabInstrument Condition Record`
                SET date_of_record = CURDATE()
                WHERE date_of_record > CURDATE()
            """)
            
            frappe.logger("migrations").info("Fixed future condition record dates")
    
    # Validate workflow state transitions
    if frappe.db.table_exists("Instrument Profile"):
        # Ensure delivered instruments have valid customer
        delivered_without_customer = frappe.db.sql("""
            SELECT name
            FROM `tabInstrument Profile`
            WHERE workflow_state = 'Delivered'
              AND (customer IS NULL OR customer = '')
        """, as_dict=True)
        
        if delivered_without_customer:
            for record in delivered_without_customer:
                frappe.db.set_value("Instrument Profile", record.name, "workflow_state", "Open")
            
            frappe.logger("migrations").info(f"Fixed {len(delivered_without_customer)} delivered instruments without customers")

def add_database_constraints():
    """Add database-level constraints for data integrity"""
    
    frappe.logger("migrations").info("Adding database constraints")
    
    try:
        # Add check constraints for valid workflow states
        if frappe.db.table_exists("Instrument Profile"):
            frappe.db.sql("""
                ALTER TABLE `tabInstrument Profile`
                ADD CONSTRAINT chk_instrument_profile_workflow_state
                CHECK (workflow_state IN ('Open', 'In Progress', 'Delivered', 'Archived'))
            """)
            frappe.logger("migrations").info("Added workflow state constraint for Instrument Profile")
    except Exception as e:
        if "Duplicate key name" not in str(e):
            frappe.logger("migrations").warning(f"Could not add constraint: {str(e)}")
    
    try:
        # Add check constraints for condition values
        if frappe.db.table_exists("Instrument Condition Record"):
            # Use backticks for `condition` column to avoid SQL reserved word issues
            frappe.db.sql("""
                ALTER TABLE `tabInstrument Condition Record`
                ADD CONSTRAINT chk_condition_record_condition
                CHECK (`condition` IN ('New', 'Good', 'Fair', 'Poor', 'Needs Repair'))
            """)
            frappe.logger("migrations").info("Added condition constraint for Instrument Condition Record")
    except Exception as e:
        if "Duplicate key name" not in str(e):
            frappe.logger("migrations").warning(f"Could not add constraint: {str(e)}")

def generate_integrity_report():
    """Generate comprehensive data integrity report"""
    
    frappe.logger("migrations").info("Generating data integrity report")
    
    report = {
        "timestamp": frappe.utils.now(),
        "tables_validated": [],
        "integrity_issues": [],
        "summary": {}
    }
    
    # Check table counts and basic statistics
    tables_to_check = [
        "Instrument Profile",
        "Instrument",
        "Instrument Model", 
        "Instrument Category",
        "Instrument Condition Record",
        "Client Instrument Profile",
        "Customer External Work Log"
    ]
    
    for table in tables_to_check:
        if frappe.db.table_exists(table):
            count = frappe.db.count(table)
            report["tables_validated"].append({
                "table": table,
                "record_count": count
            })
            
            # Check for NULL values in required fields
            if table == "Instrument Profile":
                null_serials = frappe.db.sql(f"""
                    SELECT COUNT(*) as count
                    FROM `tab{table}`
                    WHERE serial_no IS NULL OR serial_no = ''
                """)[0][0]
                
                if null_serials > 0:
                    report["integrity_issues"].append({
                        "table": table,
                        "issue": f"{null_serials} records with missing serial numbers"
                    })
    
    # Summary statistics
    total_instruments = frappe.db.count("Instrument Profile") if frappe.db.table_exists("Instrument Profile") else 0
    total_customers = frappe.db.count("Customer") if frappe.db.table_exists("Customer") else 0
    
    report["summary"] = {
        "total_instrument_profiles": total_instruments,
        "total_customers": total_customers,
        "integrity_issues_found": len(report["integrity_issues"]),
        "validation_status": "PASSED" if len(report["integrity_issues"]) == 0 else "ISSUES_FOUND"
    }
    
    # Log the report
    frappe.logger("migrations").info(f"Data Integrity Report: {report['summary']}")
    
    if report["integrity_issues"]:
        for issue in report["integrity_issues"]:
            frappe.logger("migrations").warning(f"Integrity Issue - {issue['table']}: {issue['issue']}")
    
    frappe.db.commit()
    frappe.logger("migrations").info("Data integrity validation completed successfully")