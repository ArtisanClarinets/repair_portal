# Setup Checklist Item (`setup_checklist_item`)

## Purpose
The Setup Checklist Item DocType serves as a child table to manage quality assurance checkpoints within clarinet setup projects and templates. It ensures consistent quality standards, provides completion tracking, and supports compliance documentation for setup procedures.

## Schema Summary

### Basic Information
- **DocType Type:** Child Table (`is_child_table: 1`)
- **Parent DocTypes:**
  - Setup Template (checklist_items table) - Template definitions
  - Clarinet Initial Setup (checklist table) - Project instances
- **Key Fields:**
  - `item_name` (Data): Checklist item title/description
  - `description` (Text): Detailed instructions or criteria
  - `is_mandatory` (Check): Whether item must be completed for project completion
  - `sequence` (Int): Order of checking within parent document

### Completion Tracking
- **is_completed` (Check): Whether checklist item has been completed
- **completed_by` (Link): User who marked the item complete
- **completed_date` (Datetime): When the item was completed
- **completion_notes` (Text): Notes about completion or findings

### Quality & Classification
- **priority` (Select): Priority level (Low, Medium, High, Critical)
- **category` (Select): Type of check (Visual, Functional, Measurement, Documentation)
- **expected_outcome` (Text): What should be observed/measured for success
- **tolerance` (Data): Acceptable range for measurements (if applicable)

### Validation & Review
- **requires_review` (Check): Whether completion needs supervisor review
- **reviewed_by` (Link): User who reviewed the completed item
- **review_date` (Datetime): When the item was reviewed
- **review_status` (Select): Review outcome (Approved, Rejected, Needs Rework)
- **review_notes` (Text): Reviewer comments or feedback

### Documentation
- **reference_document` (Link): Link to procedure document or specification
- **photo_required` (Check): Whether photo documentation is required
- **measurement_required` (Check): Whether measurements must be recorded
- **measurement_value` (Float): Actual measured value (if applicable)
- **measurement_uom` (Link): Unit of measure for measurement

### Links
- **User (Completed By):** Technician who completed the checklist item
- **User (Reviewed By):** Supervisor who reviewed the completion
- **File (Reference Document):** Supporting documentation or procedures
- **UOM (Measurement UOM):** Unit for measurements

## Business Rules

### Validation Hooks (Child Table Methods)
1. **validate():**
   - Validates sequence numbers are unique within parent
   - Ensures mandatory items cannot be marked as skippable
   - Validates measurement values are within tolerance if specified
   - Checks that reviewed items have review_date and reviewed_by

2. **before_insert_handler():**
   - Auto-generates sequence number if not provided
   - Sets default priority to "Medium" if not specified
   - Initializes completion tracking fields

3. **on_change():**
   - Updates parent project progress when items completed
   - Triggers notifications for mandatory item completion
   - Updates quality metrics for parent project

### Derived Fields
- **completion_percentage:** Calculated across all checklist items in parent
- **days_to_complete:** Time elapsed from parent start to item completion
- **is_overdue:** Whether item completion is behind schedule
- **quality_score:** Calculated quality rating based on completion and review

### Side Effects
- Completing mandatory items enables project progression
- Review rejections create follow-up tasks
- Critical item failures may trigger project escalation

## Checklist Categories

### Visual Inspection Items
```python
visual_checks = [
    {
        "item_name": "Pad Seating Inspection",
        "category": "Visual",
        "description": "Verify all pads are properly seated and aligned",
        "is_mandatory": 1,
        "priority": "High"
    },
    {
        "item_name": "Spring Tension Check", 
        "category": "Visual",
        "description": "Inspect spring alignment and tension consistency",
        "is_mandatory": 1,
        "priority": "Medium"
    }
]
```

### Functional Testing Items
```python
functional_checks = [
    {
        "item_name": "Key Action Test",
        "category": "Functional", 
        "description": "Test all keys for smooth operation and proper return",
        "is_mandatory": 1,
        "priority": "Critical",
        "requires_review": 1
    },
    {
        "item_name": "Register Response Test",
        "category": "Functional",
        "description": "Verify consistent response across all registers",
        "is_mandatory": 1,
        "priority": "High"
    }
]
```

### Measurement Items
```python
measurement_checks = [
    {
        "item_name": "Pad Height Measurement",
        "category": "Measurement",
        "description": "Measure pad height above tone hole",
        "measurement_required": 1,
        "measurement_uom": "Millimeter",
        "tolerance": "0.1-0.3mm",
        "is_mandatory": 1
    }
]
```

### Documentation Items
```python
documentation_checks = [
    {
        "item_name": "Setup Certificate Generation",
        "category": "Documentation",
        "description": "Generate and file setup completion certificate",
        "is_mandatory": 1,
        "priority": "Medium",
        "photo_required": 0
    }
]
```

## Completion Workflow

### Standard Completion Process
1. **Technician Completion:** Item marked complete with notes
2. **Automatic Validation:** System checks measurement tolerances
3. **Review (if required):** Supervisor reviews and approves/rejects
4. **Progress Update:** Parent project progress recalculated

### Mandatory Item Requirements
- All mandatory items must be completed before project can be submitted
- Critical mandatory items may block project progression entirely
- Failed mandatory items create corrective action requirements

### Review Process
```python
def handle_review_completion(self):
    """Process checklist item review completion"""
    if self.review_status == "Approved":
        self.mark_item_approved()
        self.update_parent_progress()
    elif self.review_status == "Rejected":
        self.create_corrective_action_task()
        self.reset_completion_status()
    elif self.review_status == "Needs Rework":
        self.create_rework_notification()
        self.set_rework_required_flag()
```

## Quality Metrics Integration

### Item-Level Metrics
- **Completion Rate:** Percentage of items completed on first attempt
- **Review Pass Rate:** Percentage of items passing review without rework
- **Time to Complete:** Average time from project start to item completion
- **Measurement Accuracy:** Variance from target measurements

### Project-Level Metrics
- **Overall Quality Score:** Weighted average of all checklist item scores
- **Mandatory Item Compliance:** Percentage of mandatory items completed
- **Review Efficiency:** Average time from completion to review
- **Rework Rate:** Percentage of items requiring rework after review

## Template vs Project Instances

### In Setup Templates
- **Purpose:** Define standard checklist items for project type
- **Behavior:** Blueprint for creating project checklist items
- **Fields Used:** item_name, description, is_mandatory, sequence, priority
- **Completion Fields:** Not used (template only)

### In Clarinet Initial Setup Projects
- **Purpose:** Track actual completion of quality checkpoints
- **Behavior:** Working checklist for project execution
- **Fields Used:** All fields including completion tracking
- **Template Sync:** Items created from template can be customized

### Synchronization Rules
```python
def sync_from_template(self, template_items):
    """Sync checklist items from template to project"""
    for template_item in template_items:
        if template_item.is_active:
            project_item = {
                "item_name": template_item.item_name,
                "description": template_item.description,
                "is_mandatory": template_item.is_mandatory,
                "sequence": template_item.sequence,
                "priority": template_item.priority,
                "category": template_item.category,
                # Completion fields initialized empty
                "is_completed": 0,
                "completion_notes": ""
            }
            self.append("checklist", project_item)
```

## Data Integrity

### Required Fields
- `item_name`: Checklist item identifier (required)
- `sequence`: Order within parent checklist (must be unique)
- `category`: Classification for organization and reporting
- `priority`: Importance level for planning and escalation

### Defaults
- `is_completed`: 0 (not completed initially)
- `is_mandatory`: 0 (optional by default)
- `priority`: "Medium" if not specified
- `requires_review`: 0 (no review required by default)
- `photo_required`: 0 (photos not required by default)
- `measurement_required`: 0 (measurements not required by default)

### Unique Constraints
- `sequence` must be unique within parent document
- Combination of `item_name` and parent should be unique

### Referential Integrity
- `completed_by`/`reviewed_by`: Must be active Users
- `reference_document`: Must be valid File attachment
- `measurement_uom`: Must exist in UOM DocType
- Parent must be valid Setup Template or Clarinet Initial Setup

### Business Constraints
- `completed_date` cannot be before parent project start date
- `review_date` must be after `completed_date`
- `measurement_value` must be within `tolerance` range if specified
- `is_completed` can only be set to 1 if required fields are filled

## Integration with Parent Projects

### Progress Calculation
```python
def calculate_checklist_progress(parent):
    """Calculate completion percentage for parent checklist"""
    total_items = len(parent.checklist)
    if total_items == 0:
        return 100.0
    
    completed_items = sum(1 for item in parent.checklist if item.is_completed)
    return (completed_items / total_items) * 100.0
```

### Mandatory Item Blocking
```python
def can_submit_project(parent):
    """Check if project can be submitted based on mandatory checklist items"""
    mandatory_items = [item for item in parent.checklist if item.is_mandatory]
    incomplete_mandatory = [item for item in mandatory_items if not item.is_completed]
    
    if incomplete_mandatory:
        frappe.throw(f"Cannot submit project. {len(incomplete_mandatory)} mandatory checklist items incomplete.")
    
    return True
```

## Reporting & Analytics

### Checklist Performance Reports
- **Completion Rate by Category:** Visual vs Functional vs Measurement vs Documentation
- **Time to Complete by Priority:** How long different priority items take
- **Review Success Rate:** Percentage passing review on first attempt
- **Technician Performance:** Completion rates and quality scores by user

### Quality Trend Analysis
- **Failure Patterns:** Which checklist items fail most frequently
- **Improvement Tracking:** Quality score trends over time
- **Template Effectiveness:** Which templates produce better quality outcomes
- **Training Needs:** Skills gaps identified from checklist failures

## Test Plan

### Checklist Item Tests
- **test_item_creation**: Valid checklist items can be created
- **test_sequence_validation**: Unique sequence numbers enforced
- **test_mandatory_logic**: Mandatory items properly enforced
- **test_measurement_validation**: Measurement tolerances validated

### Completion Workflow Tests
- **test_completion_tracking**: Items can be marked complete with proper data
- **test_review_workflow**: Review process works correctly
- **test_progress_calculation**: Parent progress updates with item completion
- **test_mandatory_blocking**: Mandatory items prevent project submission

### Template Integration Tests
- **test_template_sync**: Template items properly copied to projects
- **test_template_updates**: Changes to templates affect new projects only
- **test_custom_modifications**: Project checklist can be customized after template sync
- **test_template_versioning**: Template changes tracked and versioned

### Quality Integration Tests
- **test_quality_scoring**: Quality scores calculated correctly
- **test_failure_escalation**: Critical failures trigger appropriate escalation
- **test_corrective_actions**: Failed items create follow-up tasks
- **test_compliance_reporting**: Compliance metrics calculated accurately

## Security & Permissions

### Role-Based Access
- **Technicians:** Can complete checklist items assigned to their projects
- **Supervisors:** Can review completed items and approve/reject
- **Quality Managers:** Can modify checklist items and templates
- **Project Managers:** Can view all checklist status and metrics

### Audit Trail
- All checklist completions logged with user and timestamp
- Review decisions tracked for compliance auditing
- Changes to checklist items during project execution logged
- Quality failures and corrective actions documented

## Changelog
- 2024-01-15 – Initial creation with basic checklist functionality
- 2024-01-20 – Added review workflow and quality scoring
- 2024-01-25 – Enhanced with measurement tracking and tolerances
- 2024-02-01 – Added template synchronization and project integration
- 2024-02-05 – Integrated with quality metrics and compliance reporting