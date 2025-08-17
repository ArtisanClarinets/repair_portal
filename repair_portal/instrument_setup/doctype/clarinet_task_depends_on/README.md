# Clarinet Task Depends On (`clarinet_task_depends_on`)

## Purpose
The Clarinet Task Depends On DocType serves as a child table to manage task dependencies in both template tasks and actual project tasks. It enables complex dependency relationships, critical path analysis, and proper task sequencing in clarinet setup projects.

## Schema Summary

### Basic Information
- **DocType Type:** Child Table (`is_child_table: 1`)
- **Parent DocTypes:** 
  - Clarinet Template Task (depends_on_tasks table)
  - Clarinet Setup Task (depends_on table)
- **Key Fields:**
  - `task` (Link): Name of the task that this task depends on
  - `dependency_type` (Select): Type of dependency relationship
  - `lag_time` (Float): Delay time after prerequisite completion
  - `dependency_status` (Select): Current status of the dependency

### Dependency Configuration
- **task_name** (Data): Display name of the dependent task (read-only)
- **project** (Link): Project context for validation (read-only from parent)
- **is_critical** (Check): Whether this dependency is on the critical path
- **can_overlap** (Check): Whether tasks can run in parallel with lag

### Timing & Scheduling
- **lag_time_uom** (Select): Unit for lag time (Hours, Days, Weeks)
- **lead_time** (Float): Time this task can start before prerequisite completes
- **constraint_type** (Select): Type of scheduling constraint
- **constraint_date** (Date): Specific date constraint if applicable

### Status & Validation
- **dependency_status** (Select): Current status (Pending, Satisfied, Blocked)
- **validation_date** (Datetime): When dependency was last validated
- **notes** (Text): Additional information about the dependency relationship

### Links
- **Task:** The prerequisite task that must be completed first
- **Project:** Context project for cross-validation (inherited from parent)

## Business Rules

### Validation Hooks (Child Table Methods)
1. **validate():**
   - Prevents tasks from depending on themselves (direct circular dependency)
   - Validates that dependent task exists in same project/template
   - Ensures lag_time and lead_time are non-negative
   - Checks that dependency_type is valid for the task types involved

2. **before_insert_handler():**
   - Validates no circular dependencies will be created
   - Sets default dependency_type to "Finish-to-Start" if not specified
   - Calculates initial dependency_status based on prerequisite task status

3. **on_change():**
   - Updates parent task's dependency status
   - Recalculates project critical path if dependency is critical
   - Triggers scheduling updates for dependent tasks

### Derived Fields
- **task_name:** Fetched from linked task's subject/name
- **dependency_status:** Calculated based on prerequisite task completion
- **is_critical:** Determined by critical path analysis
- **effective_delay:** Calculated total delay including lag and lead times

### Side Effects
- Adding dependencies may delay task start dates
- Removing critical dependencies can shorten project duration
- Dependency status changes trigger task availability updates

## Dependency Types

### Finish-to-Start (FS)
- **Description:** Successor task cannot start until predecessor finishes
- **Use Case:** Standard sequential task flow
- **Example:** "Pad Installation" depends on "Old Pad Removal" finishing

### Start-to-Start (SS)
- **Description:** Successor task cannot start until predecessor starts
- **Use Case:** Parallel tasks that must begin together
- **Example:** "Quality Inspection" starts when "Setup Work" starts

### Finish-to-Finish (FF)
- **Description:** Successor task cannot finish until predecessor finishes
- **Use Case:** Tasks that must complete together
- **Example:** "Documentation" finishes when "Setup Work" finishes

### Start-to-Finish (SF)
- **Description:** Successor task cannot finish until predecessor starts (rare)
- **Use Case:** Handoff scenarios
- **Example:** "Old System Shutdown" after "New System Startup" begins

## Lag and Lead Time

### Lag Time
- **Purpose:** Mandatory delay after prerequisite completion
- **Example:** 24-hour drying time after applying adhesive
- **Calculation:** Successor start = Predecessor end + Lag time

### Lead Time  
- **Purpose:** Allow successor to start before prerequisite completes
- **Example:** Preparation work can start before materials arrive
- **Calculation:** Successor start = Predecessor end - Lead time

### Time Units
- **Hours:** For short technical delays (drying, curing)
- **Days:** For typical task scheduling
- **Weeks:** For long-term project planning

## Critical Path Integration

### Critical Path Determination
```python
def update_critical_path_status(self):
    """Update whether this dependency is on the critical path"""
    project = get_parent_project()
    critical_tasks = calculate_critical_path(project)
    
    predecessor = self.task
    successor = self.parent
    
    self.is_critical = (
        predecessor in critical_tasks and 
        successor in critical_tasks and
        self.dependency_type == "Finish-to-Start"
    )
```

### Schedule Impact Analysis
- **Critical Dependencies:** Delays directly impact project end date
- **Non-Critical Dependencies:** Have slack time available
- **Free Float:** Time dependency can be delayed without affecting successors
- **Total Float:** Time dependency can be delayed without affecting project

## Dependency Status Management

### Status Calculation
```python
def calculate_dependency_status(self):
    """Calculate current status of this dependency"""
    prerequisite_task = frappe.get_doc("Clarinet Setup Task", self.task)
    
    if prerequisite_task.status == "Completed":
        if self.lag_time > 0:
            completion_date = prerequisite_task.actual_end_date
            available_date = completion_date + timedelta(hours=self.lag_time)
            if now() >= available_date:
                return "Satisfied"
            else:
                return "Pending"
        else:
            return "Satisfied"
    elif prerequisite_task.status in ["Cancelled", "On Hold"]:
        return "Blocked"
    else:
        return "Pending"
```

### Automatic Status Updates
- **Task Completion:** Updates all dependent task statuses
- **Task Delay:** Recalculates successor availability
- **Task Cancellation:** Marks dependent tasks as blocked

## Data Integrity

### Required Fields
- `task`: Prerequisite task reference (required)
- `dependency_type`: Type of dependency relationship (required)

### Defaults
- `dependency_type`: "Finish-to-Start" (most common)
- `lag_time`: 0.0 (no delay by default)
- `lead_time`: 0.0 (no lead time by default)
- `lag_time_uom`: "Hours" (default time unit)
- `can_overlap`: 0 (no overlap by default)

### Unique Constraints
- Combination of parent task and prerequisite task must be unique
- No duplicate dependencies for same task pair

### Referential Integrity
- `task`: Must exist in appropriate task DocType (Template or Setup)
- Parent context must be valid project or template
- Circular dependencies prevented through validation

### Business Constraints
- lag_time and lead_time must be non-negative
- Task cannot depend on itself (direct or indirect)
- Dependency must be within same project/template scope
- constraint_date must be realistic for project timeline

## Circular Dependency Prevention

### Detection Algorithm
```python
def check_for_cycles(self):
    """Detect circular dependencies before creating new dependency"""
    def has_cycle(current_task, target_task, visited, rec_stack):
        visited.add(current_task)
        rec_stack.add(current_task)
        
        # Get all tasks that current_task depends on
        dependencies = get_task_dependencies(current_task)
        
        for dep_task in dependencies:
            if dep_task == target_task:
                return True  # Found cycle
            elif dep_task not in visited:
                if has_cycle(dep_task, target_task, visited, rec_stack):
                    return True
            elif dep_task in rec_stack:
                return True  # Back edge found
        
        rec_stack.remove(current_task)
        return False
    
    # Check if adding this dependency creates a cycle
    return has_cycle(self.task, self.parent, set(), set())
```

## Usage Patterns

### Standard Setup Dependencies
```python
# Typical task dependency chain for clarinet setup
standard_dependencies = [
    {
        "task": "Initial Inspection",
        "successor": "Disassembly", 
        "dependency_type": "Finish-to-Start"
    },
    {
        "task": "Disassembly",
        "successor": "Cleaning",
        "dependency_type": "Finish-to-Start"
    },
    {
        "task": "Cleaning", 
        "successor": "Pad Replacement",
        "dependency_type": "Finish-to-Start"
    }
]
```

### Parallel Task Dependencies
```python
# Tasks that can run in parallel after prerequisite
parallel_dependencies = [
    {
        "task": "Disassembly",
        "successor": "Key Cleaning",
        "dependency_type": "Finish-to-Start"
    },
    {
        "task": "Disassembly", 
        "successor": "Body Cleaning",
        "dependency_type": "Finish-to-Start"
    }
]
```

### Lag Time Dependencies
```python
# Dependencies with mandatory waiting periods
lag_dependencies = [
    {
        "task": "Apply Adhesive",
        "successor": "Install Pads", 
        "dependency_type": "Finish-to-Start",
        "lag_time": 24,
        "lag_time_uom": "Hours"
    }
]
```

## Test Plan

### Dependency Creation Tests
- **test_valid_dependency_creation**: Normal dependencies created successfully
- **test_circular_dependency_prevention**: Circular refs rejected
- **test_self_dependency_prevention**: Tasks cannot depend on themselves
- **test_cross_project_dependency_prevention**: Dependencies limited to same project

### Dependency Types Tests
- **test_finish_to_start_dependency**: Standard sequential dependencies
- **test_start_to_start_dependency**: Parallel task dependencies
- **test_finish_to_finish_dependency**: Coordinated completion dependencies
- **test_start_to_finish_dependency**: Handoff dependencies (rare)

### Timing Tests
- **test_lag_time_calculation**: Lag times properly applied to scheduling
- **test_lead_time_calculation**: Lead times allow early task starts
- **test_time_unit_conversion**: Different time units handled correctly
- **test_overlap_handling**: Task overlap permissions respected

### Status Management Tests
- **test_dependency_status_calculation**: Status calculated correctly from prerequisite
- **test_status_update_propagation**: Status changes propagate to dependent tasks
- **test_critical_path_identification**: Critical dependencies identified correctly
- **test_blocked_task_handling**: Blocked prerequisites prevent successor start

### Integration Tests
- **test_project_schedule_integration**: Dependencies affect project timeline
- **test_critical_path_calculation**: Dependencies contribute to critical path
- **test_resource_scheduling**: Dependencies considered in resource allocation
- **test_milestone_dependency_handling**: Milestone tasks properly handle dependencies

## Performance Considerations

### Large Dependency Networks
- Circular dependency checking optimized for large task sets
- Critical path calculation uses efficient graph algorithms
- Status updates batched to minimize database operations

### Real-time Updates
- Dependency status calculated on-demand when needed
- Change notifications sent asynchronously
- Schedule recalculation triggered intelligently

## Changelog
- 2024-01-15 – Initial creation with basic dependency management
- 2024-01-20 – Added circular dependency prevention and validation
- 2024-01-25 – Enhanced with lag/lead time support and critical path integration
- 2024-02-01 – Added comprehensive dependency type support
- 2024-02-05 – Optimized for performance with large dependency networks