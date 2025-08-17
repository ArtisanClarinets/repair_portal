# Clarinet Setup Task (`clarinet_setup_task`)

## Purpose
The Clarinet Setup Task DocType represents individual work items within a clarinet setup project. It mirrors ERPNext's Task DocType functionality, providing detailed task management with scheduling, dependencies, time tracking, and progress monitoring for specific operations within a Clarinet Initial Setup project.

## Schema Summary

### Task Identification & Basic Info
- **Naming:** `naming_series` = "CST-.YYYY.-.####"
- **task_id:** Unique task identifier (auto-generated)
- **subject:** Task title/description (required)
- **description:** Detailed task instructions or notes
- **task_type:** Select field (Setup, QA, Documentation, Materials)
- **priority:** Select field (Low, Medium, High, Critical)
- **status:** Select field (Open, Working, Pending Review, Completed, Cancelled)

### Project & Assignment Details
- **project:** Link to parent Clarinet Initial Setup project
- **assigned_to:** Link to User assigned to this task
- **assigned_by:** Link to User who assigned the task
- **expected_time:** Estimated hours for task completion
- **actual_time:** Actual hours logged for task completion

### Scheduling & Timeline
- **expected_start_date:** Planned task start date
- **expected_end_date:** Planned task completion date
- **actual_start_date:** Actual task start date
- **actual_end_date:** Actual task completion date

### Task Relationships
- **depends_on:** Table of Clarinet Task Depends On child records for dependencies
- **parent_task:** Link to parent task if this is a subtask
- **weight:** Numeric weight for progress calculation (default: 1)

### Progress & Quality
- **progress:** Percentage completion (0-100)
- **is_group:** Boolean indicating if this task contains subtasks
- **is_milestone:** Boolean indicating if this is a project milestone
- **review_date:** Date when task was reviewed/approved

### Links
- **Clarinet Initial Setup:** Parent project relationship
- **User (Assigned To):** Task assignee
- **User (Assigned By):** Task creator/manager
- **Parent Task:** For subtask hierarchy

### Child Tables
- **depends_on:** Links to `clarinet_task_depends_on` child table for task dependencies

## Business Rules

### Validation Hooks
1. **validate():**
   - Validates task dates (end after start, realistic duration)
   - Ensures assigned_to user has appropriate role permissions
   - Validates task dependencies don't create cycles
   - Calculates expected_end_date from start date and expected_time

2. **before_insert():**
   - Auto-generates task_id if not provided
   - Sets default status to "Open"
   - Sets assigned_by to current user if not specified
   - Validates parent project exists and is active

3. **on_update():**
   - Updates actual dates based on status changes
   - Recalculates parent project progress when task status changes
   - Sends notifications for assignment changes
   - Updates milestone tracking

4. **before_submit():**
   - Validates all dependent tasks are completed
   - Ensures actual_time is logged for completed tasks
   - Confirms task deliverables meet quality requirements

### Derived Fields
- **duration_hours:** Calculated from start/end dates or expected_time
- **completion_percentage:** Based on status and progress tracking
- **dependency_status:** Aggregated status of all dependent tasks
- **is_overdue:** Boolean based on current date vs expected_end_date

### Side Effects
- Status changes update parent project progress automatically
- Completing milestone tasks trigger project phase transitions
- Time logging updates resource utilization tracking
- Task completion may unlock dependent tasks

## Workflows

### States & Transitions
- **Open → Working:** Task started by assigned user
- **Working → Pending Review:** Task completed, awaiting approval
- **Working → Open:** Task paused or blocked
- **Pending Review → Completed:** Task approved by reviewer
- **Pending Review → Working:** Task returned for rework
- **Any State → Cancelled:** Task cancelled due to scope changes

### Actions & Roles
- **Task Assignee:** Can update status, log time, mark progress
- **Project Manager:** Can assign tasks, modify schedules, approve completion
- **QA Reviewer:** Can review completed tasks and approve or return
- **Setup Manager:** Can override task status and reassign resources

### Automatic Triggers
- **Status → Working:** Sets actual_start_date to current datetime
- **Status → Completed:** Sets actual_end_date and updates project progress
- **Milestone Completion:** Triggers project phase advancement
- **Overdue Tasks:** Generates alerts for project managers

## Client Logic (`clarinet_setup_task.js`)

### Form Events

#### `onload(frm)`
- Sets up query filters for user assignments and project links
- Configures dependency management interface
- Initializes time tracking functionality

#### `refresh(frm)`
- Shows task status and progress indicators
- Displays dependency chain and blocking tasks
- Adds custom action buttons for task management
- Shows time tracking summary and utilization

#### `validate(frm)`
- Client-side validation before save:
  - Validates date consistency and realistic timelines
  - Ensures assigned user has appropriate permissions
  - Warns about dependency conflicts

### Field-Specific Handlers

#### `status(frm)`
- **Purpose:** Handle status change side effects
- **Logic:**
  - Updates actual dates based on status transitions
  - Triggers dependency validation
  - Updates project progress calculations

#### `assigned_to(frm)`
- **Purpose:** Handle task reassignment
- **Logic:**
  - Validates new assignee has required role/permissions
  - Sends assignment notification
  - Updates resource loading calculations

#### `expected_start_date(frm)` / `expected_time(frm)`
- **Purpose:** Automatic schedule calculations
- **Logic:**
  - Calculates expected_end_date from start date and duration
  - Validates against project timeline constraints
  - Updates dependency scheduling

### Custom Action Buttons

#### Task Actions Group
- **"Start Task":** Changes status to Working and logs start time
- **"Mark Complete":** Changes status to Pending Review
- **"Log Time":** Opens time logging dialog
- **"Add Dependency":** Interface for adding task dependencies

#### Progress Tracking
- **"Update Progress":** Manual progress update with percentage
- **"Add Subtask":** Creates child task under current task
- **"View Timeline":** Shows task in project Gantt view

### Helper Functions

#### `update_task_status(frm, new_status)`
- Updates task status with appropriate validations
- Handles automatic date setting and notifications
- Updates parent project progress

#### `log_time_entry(frm, hours, description)`
- Records time spent on task with description
- Updates actual_time and progress calculations
- Provides time tracking analytics

#### `validate_dependencies(frm)`
- Checks for circular dependencies in task chain
- Validates dependency dates are consistent
- Shows dependency impact on schedule

### Child Table Events

#### Task Dependencies Table
- **Dependency addition:** Validates no circular references created
- **Dependency removal:** Checks impact on task scheduling
- **Priority ordering:** Manages critical path calculations

## Server Logic (`clarinet_setup_task.py`)

### Public/Whitelisted Methods

#### `update_status(self, status, update_modified=True)`
**Parameters:**
- `status` (str): New status value
- `update_modified` (bool): Whether to update modified timestamp

**Permissions:** Write access to task
**Purpose:** Update task status with proper validation and side effects
**Background Jobs:** None
**Returns:** Dict with updated fields and notifications sent

#### `log_time(self, hours, description="")`
**Parameters:**
- `hours` (float): Hours to log for this task
- `description` (str): Optional description of work performed

**Permissions:** Task assignee or project manager
**Purpose:** Log time spent on task and update progress
**Background Jobs:** None
**Returns:** Updated actual_time total

#### `@frappe.whitelist()` `get_dependencies(self)`
**Parameters:** None
**Permissions:** Read access to task
**Purpose:** Return all task dependencies with status information
**Background Jobs:** None
**Returns:** List of dependency objects with status details

#### `@frappe.whitelist()` `check_dependency_status(self)`
**Parameters:** None
**Permissions:** Read access to task
**Purpose:** Check if all dependencies are satisfied for task to proceed
**Background Jobs:** None
**Returns:** Dict with can_proceed boolean and blocking dependencies

### Private Helper Methods

#### `_validate_dates(self)`
- Validates date consistency and business rules
- Ensures task dates align with project timeline
- Checks dependency date constraints

#### `_update_project_progress(self)`
- Recalculates parent project progress based on task completion
- Weights tasks by expected_time for accurate progress
- Updates project milestone status

#### `_check_circular_dependencies(self)`
- Validates that adding dependencies doesn't create cycles
- Uses graph traversal to detect circular references
- Prevents invalid dependency configurations

#### `_send_status_notifications(self)`
- Sends notifications for status changes to relevant users
- Includes project manager, assignee, and dependent task owners
- Formats notifications with task context and next actions

#### `_calculate_critical_path_impact(self)`
- Determines if task is on critical path for project
- Calculates schedule impact of delays
- Updates project timeline risk indicators

## Data Integrity

### Required Fields
- `subject`: Task description (required for identification)
- `project`: Parent project reference (required)
- `status`: Current task status
- `task_type`: Type classification for reporting

### Defaults
- `status`: "Open" for new tasks
- `priority`: "Medium" if not specified
- `progress`: 0.0 for new tasks
- `weight`: 1.0 for progress calculations
- `assigned_by`: Current user creating the task

### Unique Constraints
- `task_id`: Auto-generated unique identifier per task
- No duplicate subject within same project (configurable)

### Referential Integrity
- `project`: Must exist in Clarinet Initial Setup DocType
- `assigned_to`/`assigned_by`: Must be valid active Users
- `parent_task`: Must exist and not create circular hierarchy
- Dependencies must reference valid tasks within same project

### Business Constraints
- expected_end_date must be after expected_start_date
- actual_end_date must be after actual_start_date
- progress must be between 0 and 100
- expected_time must be positive number
- Task cannot depend on itself (direct or indirect)

## Test Plan

### Task Lifecycle Tests
- **test_task_creation**: Verify tasks created with valid data
- **test_status_transitions**: Test all valid status changes
- **test_date_calculations**: Verify automatic date setting
- **test_assignment_validation**: Ensure proper user assignment

### Dependency Management Tests
- **test_dependency_creation**: Valid dependencies can be added
- **test_circular_dependency_prevention**: Circular refs rejected
- **test_dependency_status_checking**: Blocking tasks identified
- **test_critical_path_calculation**: Critical path determined correctly

### Progress Tracking Tests
- **test_progress_calculation**: Progress updates correctly
- **test_time_logging**: Time entries recorded properly
- **test_project_progress_impact**: Task completion updates project
- **test_milestone_tracking**: Milestone tasks handled correctly

### Integration Tests
- **test_project_integration**: Tasks properly linked to projects
- **test_notification_system**: Status changes trigger notifications
- **test_resource_management**: User assignments managed correctly
- **test_timeline_synchronization**: Task dates align with project

### Performance Tests
- **test_large_task_hierarchies**: Many subtasks and dependencies
- **test_concurrent_task_updates**: Multiple users updating tasks
- **test_dependency_traversal**: Large dependency graphs

### Error Handling Tests
- **test_invalid_assignments**: Non-existent or inactive users
- **test_invalid_dependencies**: Dependencies to non-existent tasks
- **test_date_validation_failures**: Invalid date combinations
- **test_permission_enforcement**: Unauthorized status changes

## Changelog
- 2024-01-15 – Initial creation with basic task management
- 2024-01-20 – Added dependency management and time tracking
- 2024-01-25 – Enhanced with milestone tracking and critical path
- 2024-02-01 – Aligned with ERPNext Task patterns and workflows
- 2024-02-05 – Added comprehensive progress tracking and notifications