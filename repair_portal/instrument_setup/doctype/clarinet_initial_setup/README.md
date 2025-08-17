# Clarinet Initial Setup (`clarinet_initial_setup`)

## Purpose
The Clarinet Initial Setup DocType serves as the main project management document for individual clarinet setup work. It mirrors ERPNext's Project DocType functionality, managing the entire lifecycle of a clarinet setup project from creation through completion, including task management, cost tracking, timeline management, and quality assurance.

## Schema Summary

### Project Identification & Basic Info
- **Naming:** `naming_series` = "CIS-.YYYY.-.####"
- **project_id:** Unique project identifier (auto-generated)
- **title:** Descriptive title for the setup project
- **setup_type:** Select field (Standard, Premium, Repair, Custom)
- **priority:** Select field (Low, Medium, High, Critical)
- **status:** Select field (Draft, Planning, In Progress, QA Review, On Hold, Completed, Cancelled)

### Instrument Details
- **instrument_profile:** Link to Instrument Profile being set up
- **clarinet_intake:** Link to originating Clarinet Intake (if applicable)
- **serial_no:** Link to Serial No for tracking
- **setup_template:** Link to Setup Template used as blueprint

### Project Details & Timeline
- **expected_start_date:** Planned project start date
- **expected_end_date:** Planned project completion date
- **actual_start_date:** Actual project start date (auto-set when status changes to In Progress)
- **actual_end_date:** Actual project completion date (auto-set when status changes to Completed)
- **progress:** Percentage completion (0-100)

### Cost Tracking & Estimation
- **estimated_cost:** Total estimated project cost
- **estimated_materials_cost:** Estimated cost of materials and parts
- **actual_cost:** Total actual project cost (calculated from materials and labor)
- **actual_materials_cost:** Actual cost of materials used
- **labor_hours:** Total labor hours worked on project

### Project Content
- **operations_performed:** Table of Setup Material Log child records
- **checklist:** Table of Setup Checklist Item child records
- **setup_tasks:** Table of Clarinet Setup Task child records

### Links
- **Instrument Profile:** One-to-one relationship to instrument being set up
- **Clarinet Intake:** Optional link to intake document that initiated setup
- **Setup Template:** Link to template used as project blueprint
- **Serial No:** Link to instrument serial number for tracking

### Child Tables
- **operations_performed:** Links to `setup_material_log` child table for material usage tracking
- **checklist:** Links to `setup_checklist_item` child table for QA checklist
- **setup_tasks:** Links to `clarinet_setup_task` child table for individual tasks

## Business Rules

### Validation Hooks
1. **validate():**
   - Validates project dates (end date after start date)
   - Ensures setup_template compatibility with instrument type
   - Calculates actual costs from child table data
   - Updates progress based on completed tasks

2. **before_insert():**
   - Auto-generates project_id if not provided
   - Sets default dates based on template estimates
   - Applies template defaults if setup_template is selected

3. **on_update():**
   - Updates actual dates when status changes
   - Recalculates costs when materials or tasks change
   - Triggers notifications for status changes

4. **before_submit():**
   - Validates all required checklist items are completed
   - Ensures actual costs are within reasonable range of estimates
   - Confirms all critical tasks are completed

### Derived Fields
- **actual_cost:** Calculated from operations_performed materials cost + (labor_hours * hourly_rate)
- **progress:** Calculated as percentage of completed setup_tasks
- **duration_days:** Calculated difference between start and end dates
- **cost_variance:** Difference between estimated and actual costs

### Side Effects
- Status changes trigger automatic date updates and notifications
- Completing setup creates entries in instrument condition records
- Submitting setup updates instrument profile status and availability

## Workflows

### States & Transitions
- **Draft → Planning:** Initial project creation and template selection
- **Planning → In Progress:** Project start with actual_start_date set
- **In Progress → QA Review:** Setup work completed, pending quality review
- **In Progress → On Hold:** Temporary pause (parts availability, customer request)
- **QA Review → Completed:** Quality approval with actual_end_date set
- **QA Review → In Progress:** Quality rejection requiring rework
- **Any State → Cancelled:** Project cancellation (customer request, damage)

### Actions & Roles
- **Setup Technician:** Can create, update, and progress projects through workflow
- **QA Manager:** Can approve completed setups or return for rework
- **Setup Manager:** Can override status changes and handle exceptions
- **Customer Service:** Can view project status and timeline information

### Automatic Triggers
- **Status → In Progress:** Sets actual_start_date to current datetime
- **Status → Completed:** Sets actual_end_date and triggers completion notifications
- **Status → On Hold:** Creates timeline entry and sends notifications
- **Progress Updates:** Automatic recalculation when tasks are completed

## Client Logic (`clarinet_initial_setup.js`)

### Form Events

#### `onload(frm)`
- Sets up query filters for all linked fields
- Configures child table queries and filters
- Initializes project management interface

#### `refresh(frm)`
- Shows project status headline and progress indicators
- Displays project timeline with expected vs actual dates
- Adds custom action buttons for project management
- Shows cost variance and budget information

#### `validate(frm)`
- Client-side validation before save:
  - Validates date consistency (end after start)
  - Ensures required fields based on status
  - Warns if costs exceed estimates significantly

### Field-Specific Handlers

#### `setup_template(frm)`
- **Purpose:** Load template defaults and create tasks/operations
- **Logic:** 
  - Calls `load_template_defaults()` to populate project fields
  - Creates child table entries from template content
  - Updates cost estimates and timeline

#### `status(frm)`
- **Purpose:** Handle status change side effects
- **Logic:**
  - Calls `update_status_indicators()` to refresh UI
  - Updates actual dates based on status transitions
  - Triggers progress recalculation

#### `expected_start_date(frm)` / `labor_hours(frm)`
- **Purpose:** Automatic timeline and cost calculations
- **Logic:**
  - Calls `calculate_expected_end_date()` for timeline updates
  - Calls `calculate_estimated_costs()` for cost updates
  - Updates related fields automatically

### Custom Action Buttons

#### Project Actions Group
- **"Start Project":** Changes status to In Progress and sets actual_start_date
- **"Mark On Hold":** Changes status to On Hold with reason tracking
- **"Send to QA":** Changes status to QA Review and notifies QA team
- **"Approve & Complete":** Final approval from QA Review to Completed
- **"Return for Rework":** QA rejection returning to In Progress

#### Template Actions
- **"Load Template Defaults":** Apply selected template to populate fields
- **"Create Tasks from Template":** Generate setup_tasks from template_tasks
- **"Create Operations from Template":** Generate operations from template

### Helper Functions

#### `load_template_defaults(frm)`
- Fetches template data and populates project fields
- Updates estimated costs and timeline from template
- Shows confirmation of loaded defaults

#### `calculate_expected_end_date(frm)`
- Calculates expected completion based on start date and labor hours
- Accounts for working days and holidays
- Updates expected_end_date field automatically

#### `calculate_estimated_costs(frm)`
- Calculates total costs from materials and labor estimates
- Updates cost fields and shows variance warnings
- Provides cost breakdown information

#### `update_status_indicators(frm)`
- Updates dashboard indicators based on current status
- Shows appropriate warnings or success messages
- Refreshes progress bars and timeline display

### Child Table Events

#### Operations Performed (Material Logs)
- **Row addition:** Updates actual costs automatically
- **Material selection:** Validates material availability and cost
- **Quantity changes:** Recalculates total material costs

#### Checklist Items
- **Completion marking:** Updates overall progress percentage
- **Critical item validation:** Prevents submission with incomplete critical items
- **Notes/comments:** Supports detailed QA documentation

#### Setup Tasks
- **Status changes:** Updates project progress automatically
- **Time tracking:** Captures actual hours vs estimates
- **Dependency management:** Prevents out-of-sequence task completion

## Server Logic (`clarinet_initial_setup.py`)

### Public/Whitelisted Methods

#### `set_defaults_from_template(self)`
**Parameters:** None
**Permissions:** Write access to document
**Purpose:** Apply setup template defaults to project fields
**Background Jobs:** None
**Returns:** Dict with applied defaults summary

#### `calculate_costs(self)`
**Parameters:** None
**Permissions:** Automatic during validation
**Purpose:** Calculate actual costs from child tables
**Background Jobs:** None
**Returns:** Dict with cost breakdown

#### `update_progress(self)`
**Parameters:** None
**Permissions:** Automatic during child table updates
**Purpose:** Recalculate project progress from task completion
**Background Jobs:** None
**Returns:** Float progress percentage (0-100)

#### `@frappe.whitelist()` `create_tasks_from_template(self)`
**Parameters:** None
**Permissions:** Write access and Setup role
**Purpose:** Generate Clarinet Setup Task documents from template
**Background Jobs:** Uses frappe.enqueue for large task sets
**Returns:** List of created task names

### Private Helper Methods

#### `_validate_project_dates(self)`
- Validates date consistency and business rules
- Ensures realistic timeline expectations
- Checks for scheduling conflicts

#### `_calculate_actual_costs(self)`
- Sums material costs from operations_performed table
- Calculates labor costs from logged hours
- Updates actual_cost and actual_materials_cost fields

#### `_update_progress_from_tasks(self)`
- Calculates completion percentage from setup_tasks
- Weights tasks by estimated hours for accuracy
- Updates progress field automatically

#### `_set_actual_dates_by_status(self)`
- Sets actual_start_date when status changes to In Progress
- Sets actual_end_date when status changes to Completed
- Logs status change history for audit

#### `_validate_completion_requirements(self)`
- Ensures all critical checklist items completed
- Validates all setup tasks in acceptable states
- Checks cost variance within acceptable limits

#### `_trigger_completion_actions(self)`
- Updates linked instrument profile status
- Creates instrument condition records
- Sends completion notifications
- Archives project materials and documentation

## Data Integrity

### Required Fields
- `title`: Descriptive project title
- `instrument_profile`: Target instrument (required for setup)
- `status`: Current project status
- `setup_type`: Type of setup being performed

### Defaults
- `status`: "Draft" for new projects
- `priority`: "Medium" if not specified  
- `progress`: 0.0 for new projects
- `expected_start_date`: Current date if not specified

### Unique Constraints
- `project_id`: Auto-generated unique identifier per project
- No duplicate active projects per instrument_profile

### Referential Integrity
- `instrument_profile`: Must exist and be available for setup
- `setup_template`: Must exist and be active
- `clarinet_intake`: If specified, must exist and be valid
- Child table tasks must have valid status values and realistic hours

### Business Constraints
- expected_end_date must be after expected_start_date
- actual_end_date must be after actual_start_date
- progress must be between 0 and 100
- actual costs should be within reasonable variance of estimates

## Test Plan

### Project Lifecycle Tests
- **test_project_creation**: Verify projects created with valid data
- **test_template_application**: Ensure template properly populates project
- **test_status_workflow**: Test all valid status transitions
- **test_date_calculations**: Verify automatic date setting logic

### Cost Calculation Tests
- **test_material_cost_calculation**: Verify material costs sum correctly
- **test_labor_cost_calculation**: Verify labor costs calculated properly
- **test_cost_variance_warnings**: Test warnings for significant variances
- **test_budget_validation**: Ensure costs stay within reasonable limits

### Progress Tracking Tests
- **test_progress_calculation**: Verify progress calculated from tasks
- **test_task_completion_impact**: Test task completion updates progress
- **test_checklist_completion**: Verify checklist affects project completion
- **test_critical_task_validation**: Test critical task completion requirements

### Integration Tests
- **test_instrument_profile_updates**: Verify setup updates instrument status
- **test_intake_integration**: Test integration with clarinet intake workflow
- **test_notification_triggers**: Verify status change notifications
- **test_timeline_updates**: Test automatic timeline management

### Performance Tests
- **test_large_project_performance**: Projects with many tasks and materials
- **test_concurrent_project_updates**: Multiple technicians updating same project
- **test_cost_calculation_performance**: Large material usage calculations

### Error Handling Tests
- **test_invalid_dates**: Invalid or inconsistent date combinations
- **test_missing_template**: Projects referencing non-existent templates
- **test_invalid_status_transitions**: Prevented status changes
- **test_completion_validation_failures**: Incomplete project submission attempts

## Changelog
- 2024-01-15 – Initial creation with basic setup tracking
- 2024-01-20 – Added template integration and task management
- 2024-01-25 – Enhanced with cost tracking and timeline features
- 2024-02-01 – Major refactoring to align with ERPNext Project patterns
- 2024-02-05 – Added comprehensive progress tracking and QA workflow