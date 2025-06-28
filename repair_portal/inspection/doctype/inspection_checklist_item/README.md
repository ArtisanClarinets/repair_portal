# Inspection Checklist Item

**Location:** repair_portal/inspection/doctype/inspection_checklist_item/

## Purpose
Child table for each individual inspection/QC step, populated by procedure or JSON template. Used in Inspection Report for QA, repair, cleaning, etc. 

## Fields
- sequence: Step number
- area: Step/checkpoint/area name
- criteria: What passes/fails
- value: Measured value (optional)
- pass_fail: Pass or Fail
- severity: Minor/Major/Critical
- corrective_action: Steps taken if failed
- photo: Required if fail
- notes: Optional

## Usage
- Auto-filled on creation of Inspection Report, based on selected procedure.
- Used to drive validation and NCR automation.

## Last Updated
2025-06-27
