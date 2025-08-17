# Clarinet Template Task Depends On (`clarinet_template_task_depends_on`)

## Purpose
The Clarinet Template Task Depends On DocType defines prerequisite relationships within setup templates, establishing which template tasks must be completed before others can begin. This ensures proper sequencing in complex setup workflows and prevents tasks from starting before their dependencies are satisfied.

## Schema Summary
- **Naming:** Auto-assigned (system managed)
- **Parent Integration:** Child table of Clarinet Template Task
- **Key Fields:**
  - `task` (Link): Reference to prerequisite Clarinet Template Task (required)
  - `parent` (Link): Parent Clarinet Template Task that depends on this prerequisite
  - `parenttype` (Data): Always "Clarinet Template Task" (system managed)
  - `parentfield` (Data): Always "depends_on" (system managed)

## Business Rules

### Dependency Logic
- **Prerequisite Validation**: Referenced task must exist and be part of the same template
- **Circular Prevention**: System prevents creating circular dependency chains
- **Sequence Enforcement**: Dependencies create implicit ordering in task execution
- **Template Propagation**: When templates are applied, these dependencies become actual task dependencies

### Relationship Requirements
- Parent task cannot depend on itself (self-reference prevention)
- All dependency tasks must belong to the same Setup Template
- Dependencies cannot span across different templates
- At least one dependency required if depends_on table is populated

## Data Structure

### Required Fields
- **`task`**: Must reference valid Clarinet Template Task
  - Enforced by Link field validation
  - Must exist in the same system
  - Cannot reference the parent task (circular prevention)

### System-Managed Fields
- **`parent`**: Automatically populated by Frappe framework
- **`parenttype`**: Always "Clarinet Template Task"
- **`parentfield`**: Always "depends_on"
- **`name`**: Auto-generated unique identifier

## Integration Points

### Template System Integration
- **Template Application**: Dependencies copied to actual Clarinet Setup Tasks when template is applied
- **Sequence Planning**: Used to calculate optimal task ordering in Gantt charts
- **Validation**: Prevents template activation if dependency chains are invalid

### Task Management Integration  
- **Status Gating**: Real tasks inherit these dependencies and cannot start until prerequisites are Complete
- **Progress Calculation**: Dependencies affect overall template progress calculation
- **Visual Representation**: Dependencies shown in task relationship diagrams

## Business Logic Implementation

### Validation Rules
Templates validate dependency relationships during save:
- No circular dependencies (A→B→A chains)
- All referenced tasks exist in the same template
- Dependencies point to valid Clarinet Template Task records
- Parent task exists and is valid

### Propagation Logic
When Setup Template is applied to create Clarinet Initial Setup:
1. Template tasks become Clarinet Setup Tasks
2. Template dependencies become Clarinet Task Depends On entries  
3. Original dependency relationships preserved in new task structure
4. Status enforcement begins immediately for real tasks

## Data Integrity

### Referential Integrity
- **Task Link**: Must reference existing Clarinet Template Task
- **Parent Relationship**: Maintained by Frappe's child table system
- **Template Scope**: All dependencies scoped to single template

### Cleanup Rules
- **Task Deletion**: If referenced task is deleted, dependency is automatically removed
- **Parent Deletion**: If parent task is deleted, all its dependencies are removed
- **Template Deletion**: All dependencies removed when template is deleted

## Usage Examples

### Linear Dependencies
```
Task A: "Inspect Instrument"
Task B: "Clean Components" (depends on A)
Task C: "Replace Pads" (depends on B) 
Task D: "Final Testing" (depends on C)
```

### Parallel Dependencies
```
Task A: "Disassemble Instrument" 
Task B: "Clean Upper Joint" (depends on A)
Task C: "Clean Lower Joint" (depends on A)
Task D: "Reassemble" (depends on B, C)
```

### Complex Dependencies
```
Task A: "Initial Inspection"
Task B: "Pad Assessment" (depends on A)
Task C: "Spring Assessment" (depends on A) 
Task D: "Replace Pads" (depends on B)
Task E: "Adjust Springs" (depends on C)
Task F: "Final Testing" (depends on D, E)
```

## Performance Considerations

### Query Optimization
- Dependencies loaded efficiently with parent tasks
- Bulk operations for template application
- Indexed relationships for fast dependency lookups

### Memory Usage
- Lightweight records with minimal data storage
- Efficient relationship representation
- Quick validation checks during task operations

## Error Handling

### Common Validation Errors
- **Circular Dependency**: "Cannot create circular dependency chain"
- **Invalid Task Reference**: "Referenced task does not exist"
- **Cross-Template Reference**: "Dependencies must be within same template"
- **Self-Reference**: "Task cannot depend on itself"

### Recovery Mechanisms
- Automatic cleanup on task deletion
- Validation repair during template save
- Dependency resolution during template application

## Test Plan

### Unit Tests
- Test circular dependency prevention
- Test valid dependency creation and deletion
- Test cross-template reference prevention
- Test propagation to real tasks

### Integration Tests
- Test template application with complex dependencies
- Test task execution with dependency gating
- Test progress calculation with dependency chains
- Test cleanup on parent task deletion

### Workflow Tests  
- Test complete setup workflow with dependencies
- Test dependency resolution in UI
- Test error handling for invalid dependencies
- Test performance with large dependency networks

## Changelog
- **2025-08-16**: Created DocType for template dependency management
- **Initial**: Basic dependency relationship structure

## Dependencies
- **Frappe Framework**: Child table management, referential integrity
- **Parent DocType**: Clarinet Template Task (contains dependency definitions)
- **Referenced DocType**: Clarinet Template Task (prerequisite tasks)
- **Propagation Target**: Clarinet Task Depends On (runtime dependency implementation)
