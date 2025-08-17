# Clarinet Setup Operation (`clarinet_setup_operation`)

## Purpose
The Clarinet Setup Operation DocType serves as a child table to capture specific technical operations performed during clarinet setup projects. It provides granular tracking of individual repair and adjustment activities, enabling precise documentation of work performed, progress monitoring, and quality control verification.

## Schema Summary

### Basic Information
- **DocType Type:** Child Table (`istable: 1`)
- **Naming:** Auto-formatted as `CSO-{#####}` (sequential numbering)
- **Parent DocTypes:** Used in various setup-related master documents
- **Engine:** InnoDB for transaction safety

### Operation Classification
- **`operation_type`** (Select): Type of technical operation performed (required, in list/filter views)
  - Options: Tone Hole Reaming, Tone Hole Repair, Chimney Leak, Tenon Fitting, Key Height Adjustment, Spring Tension Adjustment, Pad Leveling, Cork Replacement, Setup, Other
- **`section`** (Select): Physical section of instrument where work performed (in list/filter views)
  - Options: All, Mouthpiece, Barrel, Upper Joint, Lower Joint, Bell

### Operation Details
- **`component_ref`** (Data): Specific component reference (e.g., tone hole number, key name) (in list/filter views)
- **`details`** (Text): Detailed notes about the operation performed
- **`completed`** (Check): Whether the operation has been completed (defaults to 0, in list view)

## Operation Types & Classifications

### Tone Hole Operations
```python
tone_hole_operations = [
    {
        "operation_type": "Tone Hole Reaming",
        "section": "Upper Joint", 
        "component_ref": "Tone Hole #3",
        "details": "Reamed tone hole to 14.2mm diameter for proper pad seating",
        "completed": 1
    },
    {
        "operation_type": "Tone Hole Repair",
        "section": "Lower Joint",
        "component_ref": "Tone Hole #12", 
        "details": "Filled and re-drilled cracked tone hole. Applied epoxy repair.",
        "completed": 1
    },
    {
        "operation_type": "Chimney Leak",
        "section": "Upper Joint",
        "component_ref": "Register Key Chimney",
        "details": "Sealed hairline crack in register key chimney with specialized adhesive",
        "completed": 1
    }
]
```

### Mechanical Adjustments
```python
mechanical_operations = [
    {
        "operation_type": "Key Height Adjustment", 
        "section": "Lower Joint",
        "component_ref": "RH1 Key (B)",
        "details": "Adjusted key height to 2.8mm above tone hole for optimal response",
        "completed": 1
    },
    {
        "operation_type": "Spring Tension Adjustment",
        "section": "Upper Joint", 
        "component_ref": "G# Key Spring",
        "details": "Increased spring tension 15% to improve key return speed",
        "completed": 1
    },
    {
        "operation_type": "Tenon Fitting",
        "section": "All",
        "component_ref": "Upper-Lower Joint Connection", 
        "details": "Fitted tenon cork for proper joint alignment and air seal",
        "completed": 1
    }
]
```

### Pad and Cork Operations
```python
pad_cork_operations = [
    {
        "operation_type": "Pad Leveling",
        "section": "Upper Joint",
        "component_ref": "Thumb Hole Pad",
        "details": "Leveled pad surface using heat and pressure adjustment technique",
        "completed": 1
    },
    {
        "operation_type": "Cork Replacement", 
        "section": "Upper Joint",
        "component_ref": "Thumb Rest Cork",
        "details": "Replaced worn thumb rest cork with 3mm natural cork",
        "completed": 1
    }
]
```

### General Setup Operations
```python
general_operations = [
    {
        "operation_type": "Setup",
        "section": "All",
        "component_ref": "Complete Instrument",
        "details": "Full setup including pad adjustment, spring tuning, and regulation",
        "completed": 1
    },
    {
        "operation_type": "Other",
        "section": "Bell", 
        "component_ref": "Bell Ring",
        "details": "Polished and protective coating applied to bell exterior",
        "completed": 0
    }
]
```

## Business Rules

### Operation Sequencing
- Operations should be performed in logical sequence (disassembly → repair → adjustment → reassembly)
- Some operations have prerequisites (pad leveling requires pad replacement first)
- Section-specific operations should be grouped for efficiency
- Final setup operations typically performed last

### Completion Tracking
```python
def validate_completion(self):
    """Validate operation completion requirements"""
    if self.completed:
        if not self.details or len(self.details.strip()) < 10:
            frappe.throw("Completed operations must have detailed notes (minimum 10 characters)")
        
        # Some operations require specific validation
        if self.operation_type == "Pad Leveling":
            if "leak test" not in self.details.lower():
                frappe.throw("Pad leveling operations must include leak test verification")
```

### Quality Standards
- All operations must include sufficient detail for quality review
- Critical operations (tone hole work, pad adjustments) require supervisor verification
- Measurements must be recorded where applicable
- Before/after photos recommended for major repairs

### Progress Calculation
```python
def calculate_operation_progress(parent_doc):
    """Calculate completion percentage for operation list"""
    if not hasattr(parent_doc, 'operations') or not parent_doc.operations:
        return 0.0
    
    total_ops = len(parent_doc.operations)
    completed_ops = sum(1 for op in parent_doc.operations if op.completed)
    
    return (completed_ops / total_ops) * 100.0
```

## Integration Points

### Setup Project Integration
- Operations feed into overall project progress calculation
- Completed operations enable downstream workflow steps
- Operation details included in setup certificates and documentation
- Time tracking can be associated with specific operations

### Quality Control Integration
```python
def generate_qc_checklist(operations):
    """Generate quality control checklist from completed operations"""
    qc_items = []
    
    for op in operations:
        if op.completed and op.operation_type in ["Pad Leveling", "Tone Hole Repair", "Key Height Adjustment"]:
            qc_items.append({
                "check_item": f"Verify {op.operation_type} on {op.component_ref}",
                "section": op.section,
                "reference_operation": op.name,
                "expected_outcome": get_qc_criteria(op.operation_type)
            })
    
    return qc_items
```

### Inventory Integration
- Operations trigger parts/materials consumption recording
- Cork replacement operations update inventory levels
- Tool usage tracked with specific operations
- Specialized materials (adhesives, lubricants) consumed per operation

### Documentation Integration
- Operation details feed into customer work summaries
- Technical specifications included in setup certificates
- Warranty documentation references completed operations
- Service history updated with operation details

## Section-Specific Guidelines

### Mouthpiece Operations
- Limited operations typically performed on customer mouthpieces
- Focus on cleaning, minor adjustments, and cork replacement
- Interface adjustments for proper barrel fit
- Tip/facing work requires specialized tools and expertise

### Barrel Operations
- Tenon/socket fitting adjustments
- Cork replacement for proper joint sealing
- Cleaning and bore maintenance
- Crack repair if needed

### Upper Joint Operations (Most Complex)
- Tone hole work (reaming, repair, leveling)
- Key mechanism adjustments (height, spring tension)
- Pad replacement and leveling
- Register key and thumb hole maintenance
- Complex key mechanism regulation

### Lower Joint Operations
- Tone hole maintenance (typically fewer holes than upper joint)
- Key mechanism work (especially LH pinky keys)
- Bridge key adjustments
- Joint socket maintenance

### Bell Operations
- Bell key operations (if equipped)
- Tenon fitting adjustments
- Cosmetic work (polishing, protective coating)
- Extended range key work (low Eb, low D, low C if present)

## Operation Standards by Type

### Tone Hole Reaming
- **Precision:** ±0.05mm tolerance
- **Documentation:** Original and final diameters recorded
- **Quality Check:** Pad seating test after reaming
- **Tools:** Precision reamers, calipers, pad seating compound

### Key Height Adjustment
- **Standards:** Manufacturer specifications or established optimal heights
- **Measurement:** Digital calipers or specialized gauges
- **Documentation:** Before/after measurements recorded
- **Quality Check:** Action test, response verification

### Pad Leveling  
- **Technique:** Heat adjustment or mechanical leveling
- **Verification:** Leak light test, cigarette paper test
- **Documentation:** Leveling method and results
- **Quality Check:** Air seal verification across entire pad

### Spring Adjustment
- **Method:** Tension adjustment, spring replacement if needed
- **Documentation:** Adjustment direction and amount
- **Testing:** Key action test, return speed verification
- **Quality Check:** Consistent action across all affected keys

## Error Prevention

### Common Mistakes Prevention
```python
def validate_operation_logic(self):
    """Prevent common operation sequence errors"""
    # Component reference validation
    if self.section == "Mouthpiece" and "tone hole" in self.component_ref.lower():
        frappe.throw("Mouthpieces do not have tone holes - check section assignment")
    
    # Operation type validation  
    if self.operation_type == "Tenon Fitting" and self.section not in ["All", "Upper Joint", "Lower Joint", "Barrel"]:
        frappe.throw("Tenon fitting only applies to joints with tenons")
    
    # Completion logic
    if self.completed and not self.details:
        frappe.throw("Completed operations must include detailed work notes")
```

### Quality Gates
- Critical operations require supervisor sign-off
- Measurement-dependent operations must include actual measurements
- Before/after documentation required for major repairs
- Customer approval needed for operations beyond original scope

## Reporting Applications

### Technical Work Summary
```python
def generate_technical_summary(operations):
    """Generate customer-friendly technical work summary"""
    summary = {
        "tone_hole_work": filter_operations(operations, ["Tone Hole Reaming", "Tone Hole Repair"]),
        "mechanical_adjustments": filter_operations(operations, ["Key Height Adjustment", "Spring Tension Adjustment"]),
        "pad_work": filter_operations(operations, ["Pad Leveling", "Cork Replacement"]),
        "general_setup": filter_operations(operations, ["Setup"])
    }
    return summary
```

### Quality Metrics
- Operation completion rate by technician
- Average time per operation type
- Quality review pass rate by operation
- Customer satisfaction correlation with operation detail level

### Efficiency Analysis
- Most common operations by instrument type
- Time estimates vs actual completion time
- Resource utilization by operation type
- Technician specialization patterns

## Performance Considerations

### Data Volume Management
- Operations are child records - efficient bulk operations needed
- Indexing on operation_type and section for fast filtering
- Archive old operations while preserving audit trail
- Efficient reporting queries across large operation datasets

### Memory Usage
- Light-weight records with minimal data storage
- Efficient filtering and searching capabilities
- Bulk update operations for status changes
- Optimized joins with parent documents

## Test Plan

### Operation Management Tests
- **test_operation_creation:** Valid operations can be created with proper validation
- **test_completion_workflow:** Operations can be marked complete with proper validation
- **test_section_component_logic:** Section/component combinations validated properly
- **test_operation_sequencing:** Operations follow logical sequence rules

### Integration Tests
- **test_progress_calculation:** Operations properly update parent project progress
- **test_qc_integration:** Quality control items generated from completed operations  
- **test_inventory_integration:** Operations trigger proper inventory adjustments
- **test_documentation_integration:** Operations feed into certificates and reports

### Quality Tests
- **test_completion_validation:** Completed operations have sufficient detail
- **test_measurement_recording:** Operations requiring measurements properly validated
- **test_quality_gates:** Critical operations trigger appropriate review requirements
- **test_audit_trail:** All operation changes properly tracked and logged

### Performance Tests
- **test_bulk_operations:** Efficient handling of many operations per project
- **test_reporting_queries:** Fast report generation from operation data
- **test_search_filtering:** Quick operation search and filter performance
- **test_archival_operations:** Old operations efficiently archived without performance impact

## Security & Audit

### Access Control
- Operations inherit parent document permissions
- Technicians can complete operations assigned to them
- Supervisors can review and modify operations
- Quality managers have read access for auditing

### Audit Trail  
- All operation modifications tracked with user and timestamp
- Completion status changes logged for compliance
- Quality review actions recorded for audit
- Integration with broader quality management system

## Changelog
- **2025-08-17** – Initial comprehensive documentation
- **2025-08-17** – Added operation types and quality standards  
- **2025-08-17** – Integrated with setup workflow and quality control
- **2025-08-17** – Added reporting and analytics capabilities