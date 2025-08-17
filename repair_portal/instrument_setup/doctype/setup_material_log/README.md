# Setup Material Log (`setup_material_log`)

## Purpose
The Setup Material Log DocType serves as a child table for tracking materials, parts, and supplies used during clarinet setup operations. It provides detailed consumption tracking, cost calculation, and inventory integration for project cost management and material planning.

## Schema Summary

### Basic Information
- **DocType Type:** Child Table (`is_child_table: 1`)
- **Parent DocTypes:** Clarinet Initial Setup (operations_performed table)
- **Key Fields:**
  - `item` (Link): Item/part used from inventory
  - `quantity` (Float): Quantity consumed
  - `uom` (Link): Unit of measure for quantity
  - `rate` (Currency): Cost per unit
  - `amount` (Currency): Total cost (quantity × rate)

### Material Details
- **item_code:** Item code from linked Item
- **item_name:** Item description from linked Item
- **warehouse:** Link to Warehouse where item was consumed from
- **batch_no:** Link to Batch No for batch-tracked items
- **serial_no:** Link to Serial No for serialized items

### Usage Context
- **operation_type:** Select field (Standard Setup, Premium Setup, Repair, Custom)
- **usage_notes:** Text field for notes about material usage
- **technician:** Link to User who consumed the material
- **usage_date:** Date when material was consumed

### Cost & Valuation
- **standard_rate:** Standard cost from Item master
- **actual_rate:** Actual cost charged to project
- **cost_variance:** Difference between standard and actual rates
- **is_billable:** Boolean indicating if cost should be billed to customer

### Links
- **Item:** Material/part consumed from inventory
- **Warehouse:** Source warehouse for material consumption
- **Batch No:** For batch-tracked inventory items
- **Serial No:** For serialized inventory items
- **UOM:** Unit of measure for quantity tracking
- **User (Technician):** Person who consumed the material

## Business Rules

### Validation Hooks (Child Table Methods)
1. **validate():**
   - Validates item exists and is active
   - Ensures quantity is positive
   - Calculates amount from quantity and rate
   - Validates warehouse has sufficient stock

2. **before_insert_handler():**
   - Fetches standard rate from Item master
   - Sets default UOM from Item if not specified
   - Validates warehouse permissions for technician

3. **on_change():**
   - Updates parent project actual_materials_cost
   - Triggers inventory consumption if auto_consume enabled
   - Recalculates project cost variance

### Derived Fields
- **amount:** Calculated as quantity × rate
- **cost_variance:** Difference between standard_rate and actual_rate
- **item_code:** Fetched from linked Item
- **item_name:** Fetched from linked Item description

### Side Effects
- Material consumption updates inventory stock levels
- Cost changes trigger parent project cost recalculation
- Batch/serial consumption updates tracking records

## Data Integrity

### Required Fields
- `item`: Material/part being consumed (required)
- `quantity`: Amount consumed (must be > 0)
- `uom`: Unit of measure for quantity
- `rate`: Cost per unit (must be ≥ 0)

### Defaults
- `uom`: Default UOM from Item master
- `rate`: Standard rate from Item master
- `usage_date`: Current date
- `technician`: Current user if has appropriate role

### Referential Integrity
- `item`: Must exist in Item DocType and be active
- `warehouse`: Must exist and have stock for the item
- `batch_no`: Must exist and belong to the specified item
- `serial_no`: Must exist, be active, and belong to the item
- `technician`: Must be active User with technician role

### Business Constraints
- quantity must be positive number
- rate must be non-negative
- usage_date cannot be future date
- batch/serial items require valid batch_no/serial_no
- warehouse must have sufficient stock for non-negative inventory

## Parent DocType Integration

### Clarinet Initial Setup Integration
- **operations_performed Table:** Contains Setup Material Log child records
- **Cost Calculation:** Parent actual_materials_cost calculated from sum of amounts
- **Progress Tracking:** Material consumption indicates operation progress
- **Inventory Impact:** Stock consumption tracked against project budget

### Parent Methods Called
- **recalculate_costs():** Triggered when material costs change
- **update_progress():** Material usage may indicate task completion
- **validate_budget():** Ensures material costs stay within project budget

## Usage Patterns

### Standard Setup Materials
```python
# Common materials for standard clarinet setup
materials = [
    {"item": "Clarinet Pad Set - Standard", "quantity": 1, "operation_type": "Standard Setup"},
    {"item": "Cork Grease", "quantity": 0.1, "uom": "Tube", "operation_type": "Standard Setup"},
    {"item": "Key Oil", "quantity": 0.05, "uom": "Bottle", "operation_type": "Standard Setup"}
]
```

### Premium Setup Materials
```python
# Enhanced materials for premium setup
materials = [
    {"item": "Clarinet Pad Set - Premium", "quantity": 1, "operation_type": "Premium Setup"},
    {"item": "Resonance Tuning Kit", "quantity": 1, "operation_type": "Premium Setup"},
    {"item": "Professional Cork Set", "quantity": 1, "operation_type": "Premium Setup"}
]
```

### Repair-Specific Materials
```python
# Materials for specific repair operations
repair_materials = [
    {"item": "Replacement Spring Set", "quantity": 1, "operation_type": "Repair"},
    {"item": "Tone Hole Leveling Compound", "quantity": 0.2, "uom": "Gram", "operation_type": "Repair"}
]
```

## Inventory Integration

### Stock Movement
- Material consumption creates Stock Ledger Entries
- Warehouse stock levels updated in real-time
- Batch and serial tracking maintained through consumption

### Cost Accounting
- Standard costing vs actual costing supported
- Cost variances tracked for analysis
- Project profitability calculated accurately

### Reorder Management
- Low stock alerts triggered by consumption
- Automatic reorder points maintained
- Supplier management integrated with procurement

## Reporting & Analytics

### Cost Analysis
- Material cost per project type
- Cost variance analysis by technician
- Budget vs actual material consumption

### Usage Patterns
- Most consumed materials by setup type
- Technician efficiency in material usage
- Seasonal demand patterns for materials

### Inventory Insights
- Fast-moving vs slow-moving materials
- Stock turnover rates by material category
- Supplier performance for material quality

## Test Plan

### Validation Tests
- **test_material_validation**: Valid items and quantities
- **test_cost_calculation**: Amount calculations correct
- **test_inventory_validation**: Sufficient stock checks
- **test_batch_serial_tracking**: Proper tracking for applicable items

### Integration Tests
- **test_parent_cost_update**: Parent costs recalculated correctly
- **test_inventory_consumption**: Stock levels updated properly
- **test_batch_consumption**: Batch quantities decremented
- **test_serial_consumption**: Serial numbers marked as consumed

### Business Logic Tests
- **test_uom_conversion**: Quantities converted correctly between UOMs
- **test_cost_variance_calculation**: Variance calculations accurate
- **test_billable_flag_handling**: Billable vs non-billable costs
- **test_usage_date_validation**: Date validations work correctly

### Performance Tests
- **test_bulk_material_consumption**: Many materials consumed at once
- **test_concurrent_updates**: Multiple technicians logging materials
- **test_cost_calculation_performance**: Large projects with many materials

## Security Considerations

### Access Control
- Only assigned technicians can log materials for their tasks
- Project managers can view and modify all material logs
- Inventory managers can override rates and validate consumption

### Audit Trail
- All material consumption logged with user and timestamp
- Cost changes tracked for financial audit
- Inventory movements fully auditable

### Data Privacy
- No PII in material consumption records
- Cost information restricted to authorized roles
- Material usage patterns not exposed to external parties

## Changelog
- 2024-01-15 – Initial creation with basic material tracking
- 2024-01-20 – Added inventory integration and cost calculations
- 2024-01-25 – Enhanced with batch/serial tracking support
- 2024-02-01 – Added cost variance analysis and reporting
- 2024-02-05 – Integrated with project budget and profitability tracking