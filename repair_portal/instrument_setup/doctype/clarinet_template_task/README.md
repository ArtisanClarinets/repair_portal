# Clarinet Template Task (`clarinet_template_task`)

## Purpose
The Clarinet Template Task DocType serves as a child table within Setup Templates to define task blueprints that will be instantiated as actual Clarinet Setup Tasks when a template is applied to a project. It enables standardized task definitions with dependencies, time estimates, and sequencing.

## Schema Summary

### Basic Information
- **DocType Type:** Child Table (`is_child_table: 1`)
- **Parent DocTypes:** Setup Template (template_tasks table)
- **Key Fields:**
  - `task_name` (Data): Template task identifier/title
  - `subject` (Data): Detailed task description
  - `task_type` (Select): Type of task (Setup, QA, Documentation, Materials)
  - `sequence` (Int): Order of execution within template

### Time & Resource Estimation
- **estimated_hours** (Float): Expected time to complete task
- **assigned_role** (Link): Default role for task assignment
- **priority** (Select): Task priority (Low, Medium, High, Critical)
- **is_milestone** (Check): Whether task represents a project milestone

### Task Configuration
- **depends_on_tasks** (Table): Child table of Clarinet Template Task Depends On
- **description** (Text): Detailed task instructions
- **deliverable** (Data): Expected outcome/deliverable from task
- **quality_criteria** (Text): Acceptance criteria for task completion

### Template Metadata
- **is_active** (Check): Whether task is included in new projects
- **is_mandatory** (Check): Whether task is required for project completion
- **can_skip** (Check): Whether task can be skipped under certain conditions
- **skip_conditions** (Text): Conditions under which task can be skipped

### Links
- **Role (Assigned Role):** Default role for task assignment
- **Setup Template:** Parent template containing this task blueprint

### Child Tables
- **depends_on_tasks:** Links to `clarinet_template_task_depends_on` child table for dependencies

## Business Rules

### Validation Hooks (Child Table Methods)
1. **validate():**
   - Validates sequence numbers are unique within template
   - Ensures task dependencies don't create circular references
   - Validates estimated_hours is positive
   - Checks that mandatory tasks cannot be skipped

2. **before_insert_handler():**
   - Auto-generates sequence number if not provided
   - Sets default priority to "Medium" if not specified
   - Validates assigned_role has appropriate permissions

3. **on_change():**
   - Updates template complexity metrics
   - Recalculates template estimated duration
   - Validates dependency consistency across template

### Derived Fields
- **dependency_count:** Number of tasks this task depends on
- **dependent_task_count:** Number of tasks that depend on this task
- **is_critical_path:** Boolean indicating if task is on critical path
- **template_position:** Calculated position in template sequence

### Side Effects
- Adding/removing tasks updates parent template estimated hours
- Dependency changes may affect template critical path
- Mandatory task changes affect template completion requirements

## Task Instantiation

### When Template Applied to Project
1. **Task Creation:** Each template task creates a Clarinet Setup Task
2. **Dependency Mapping:** Template dependencies become task dependencies
3. **Assignment:** Tasks assigned based on assigned_role
4. **Scheduling:** Tasks scheduled based on sequence and dependencies

### Field Mapping to Clarinet Setup Task
```python
template_to_task_mapping = {
    "task_name": "subject",
    "subject": "description", 
    "estimated_hours": "expected_time",
    "priority": "priority",
    "is_milestone": "is_milestone",
    "assigned_role": "assigned_to",  # Resolved to specific user
    "sequence": "task_order"
}
```

## Data Integrity

### Required Fields
- `task_name`: Unique identifier within template (required)
- `subject`: Task description for clarity (required)
- `sequence`: Execution order (must be unique within template)
- `task_type`: Classification for organization and reporting

### Defaults
- `priority`: "Medium" if not specified
- `is_active`: 1 (included in new projects)
- `is_mandatory`: 0 (can be optional)
- `can_skip`: 0 (cannot be skipped by default)
- `estimated_hours`: 1.0 if not provided

### Unique Constraints
- `task_name` must be unique within parent template
- `sequence` must be unique within parent template

### Referential Integrity
- `assigned_role`: Must exist in Role DocType
- Dependencies must reference valid tasks within same template
- Parent template must exist and be active

### Business Constraints
- sequence must be positive integer
- estimated_hours must be positive number
- mandatory tasks cannot have can_skip = 1
- circular dependencies not allowed in task chain

## Template Task Dependencies

### Dependency Management
- **Linear Dependencies:** Task B starts after Task A completes
- **Parallel Dependencies:** Multiple tasks can depend on single predecessor
- **Milestone Dependencies:** Milestone tasks can gate subsequent phases

### Dependency Validation
```python
def validate_dependencies(self):
    """Prevent circular dependencies in template tasks"""
    visited = set()
    rec_stack = set()
    
    def has_cycle(task_name):
        visited.add(task_name)
        rec_stack.add(task_name)
        
        for dep in get_dependencies(task_name):
            if dep not in visited:
                if has_cycle(dep):
                    return True
            elif dep in rec_stack:
                return True
                
        rec_stack.remove(task_name)
        return False
```

## Quality & Completion Criteria

### Task Acceptance
- **Quality Criteria:** Defined acceptance standards
- **Deliverables:** Expected outputs from task
- **Review Process:** Who reviews and approves task completion

### Milestone Tasks
- **Project Gates:** Major decision points in project lifecycle
- **Phase Transitions:** Moving between project phases
- **Quality Gates:** QA checkpoints before proceeding

## Template Optimization

### Critical Path Analysis
- **Duration Calculation:** Longest path through dependent tasks
- **Resource Optimization:** Balancing task assignments
- **Schedule Compression:** Identifying opportunities to reduce duration

### Template Metrics
- **Complexity Score:** Based on task count and dependencies
- **Estimated Duration:** Total hours from critical path
- **Resource Requirements:** Roles and skills needed
- **Risk Assessment:** Tasks with high uncertainty or complexity

## Usage Patterns

### Standard Setup Template Tasks
```python
standard_tasks = [
    {
        "sequence": 1,
        "task_name": "Initial Inspection",
        "subject": "Perform initial instrument inspection and assessment",
        "task_type": "Setup",
        "estimated_hours": 1.0,
        "is_mandatory": 1
    },
    {
        "sequence": 2,
        "task_name": "Pad Replacement",
        "subject": "Replace clarinet pads according to specifications",
        "task_type": "Setup", 
        "estimated_hours": 4.0,
        "depends_on": ["Initial Inspection"]
    }
]
```

### Premium Setup Template Tasks
```python
premium_tasks = [
    {
        "sequence": 1,
        "task_name": "Advanced Inspection",
        "subject": "Comprehensive inspection including tone hole analysis",
        "task_type": "Setup",
        "estimated_hours": 2.0,
        "is_mandatory": 1
    },
    {
        "sequence": 2,
        "task_name": "Precision Pad Fitting",
        "subject": "Custom fit pads with precision measurements",
        "task_type": "Setup",
        "estimated_hours": 6.0,
        "assigned_role": "Senior Technician"
    }
]
```

## Test Plan

### Template Task Tests
- **test_task_creation**: Valid template tasks can be created
- **test_sequence_validation**: Unique sequence numbers enforced
- **test_dependency_validation**: Circular dependencies prevented
- **test_mandatory_task_logic**: Mandatory tasks properly handled

### Dependency Tests
- **test_linear_dependencies**: Sequential task dependencies work
- **test_parallel_dependencies**: Multiple dependencies handled correctly
- **test_circular_dependency_prevention**: Cycles detected and prevented
- **test_dependency_deletion_impact**: Removing dependencies handled safely

### Template Application Tests
- **test_task_instantiation**: Template tasks create proper Clarinet Setup Tasks
- **test_dependency_mapping**: Dependencies properly transferred to actual tasks
- **test_role_assignment**: Assigned roles resolved to actual users
- **test_milestone_handling**: Milestone tasks properly flagged

### Validation Tests
- **test_estimated_hours_validation**: Hours must be positive
- **test_role_validation**: Assigned roles must exist and be valid
- **test_skip_conditions**: Skip logic works correctly
- **test_quality_criteria_requirements**: Quality standards enforced

## Integration Considerations

### Setup Template Integration
- Template tasks contribute to overall template complexity
- Task changes trigger template recalculation
- Template activation requires valid task configuration

### Project Creation Integration  
- Template application creates corresponding Clarinet Setup Tasks
- Dependencies preserved during task instantiation
- Resource assignments translated from roles to users

### Reporting Integration
- Template effectiveness measured by actual vs estimated hours
- Task completion rates tracked across template usage
- Resource utilization analyzed by template task type

## Changelog
- 2024-01-15 – Initial creation with basic task template structure
- 2024-01-20 – Added dependency management and sequencing
- 2024-01-25 – Enhanced with quality criteria and milestone support
- 2024-02-01 – Added role-based assignment and skip conditions
- 2024-02-05 – Integrated with critical path analysis and optimization