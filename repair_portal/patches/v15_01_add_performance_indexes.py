import frappe


def execute():
    """
    Add database indexes for instrument_setup module performance optimization.
    Idempotent patch that can be run multiple times safely.
    """
    # Dictionary of table name -> list of (field_names, index_name)
    indexes_to_create = {
        "Clarinet Initial Setup": [
            (["status"], "idx_clarinet_initial_setup_status"),
            (["setup_template"], "idx_clarinet_initial_setup_template"),
            (["technician"], "idx_clarinet_initial_setup_technician"),
            (["expected_start_date"], "idx_clarinet_initial_setup_start_date"),
            (["actual_end_date"], "idx_clarinet_initial_setup_end_date"),
            (["instrument"], "idx_clarinet_initial_setup_instrument"),
            (["priority"], "idx_clarinet_initial_setup_priority"),
        ],
        "Clarinet Setup Task": [
            (["clarinet_initial_setup"], "idx_clarinet_setup_task_parent"),
            (["status"], "idx_clarinet_setup_task_status"),
            (["priority"], "idx_clarinet_setup_task_priority"),
            (["assigned_to"], "idx_clarinet_setup_task_assigned"),
            (["exp_start_date"], "idx_clarinet_setup_task_start_date"),
            (["sequence"], "idx_clarinet_setup_task_sequence"),
        ],
        "Clarinet Task Depends On": [
            (["task"], "idx_clarinet_task_depends_task"),
            (["parent"], "idx_clarinet_task_depends_parent"),
        ],
        "Clarinet Pad Map": [
            (["clarinet_model"], "idx_clarinet_pad_map_model"),
        ],
        "Setup Template": [
            (["clarinet_model"], "idx_setup_template_model"),
            (["is_active"], "idx_setup_template_active"),
            (["setup_type"], "idx_setup_template_type"),
        ],
        "Clarinet Template Task": [
            (["parent"], "idx_clarinet_template_task_parent"),
            (["sequence"], "idx_clarinet_template_task_sequence"),
        ],
        "Setup Material Log": [
            (["parent"], "idx_setup_material_log_parent"),
            (["material_type"], "idx_setup_material_log_type"),
        ],
        "Clarinet Setup Operation": [
            (["parent"], "idx_clarinet_setup_operation_parent"),
            (["operation_type"], "idx_clarinet_setup_operation_type"),
            (["section"], "idx_clarinet_setup_operation_section"),
        ],
    }
    
    created_indexes = []
    skipped_indexes = []
    
    for table_name, indexes in indexes_to_create.items():
        if not frappe.db.table_exists(table_name):
            continue
            
        for fields, index_name in indexes:
            try:
                # Check if index already exists
                if frappe.db.db_type == "mariadb":
                    existing = frappe.db.sql("""
                        SELECT COUNT(*) 
                        FROM INFORMATION_SCHEMA.STATISTICS 
                        WHERE TABLE_SCHEMA = %s 
                        AND TABLE_NAME = %s 
                        AND INDEX_NAME = %s
                    """, (frappe.db.get_database_name(), f"tab{table_name}", index_name))
                    
                    if existing[0][0] > 0:
                        skipped_indexes.append(f"{table_name}.{index_name}")
                        continue
                
                # Create the index
                frappe.db.add_index(table_name, fields, index_name)
                created_indexes.append(f"{table_name}.{index_name}")
                
            except Exception as e:
                frappe.log_error(f"Failed to create index {index_name} on {table_name}: {str(e)}")
    
    if created_indexes:
        frappe.log(f"Created indexes: {', '.join(created_indexes)}")
    
    if skipped_indexes:
        frappe.log(f"Skipped existing indexes: {', '.join(skipped_indexes)}")