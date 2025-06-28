# Inspection Report

**Location:** repair_portal/inspection/doctype/inspection_report/

## Purpose
Master DocType for all inspection events: QA, repair, cleaning, modification, and upgrades. Centralizes instrument history.

## Key Fields
- inspection_type: QA, cleaning, repair, etc.
- procedure: Quality Procedure (ERPNext-linked)
- status: Scheduled, In Progress, Pending Review, Passed, Failed
- inspection_checklist: Auto-populated checklist (Inspection Checklist Item)
- inspection_findings: Freeform findings (Inspection Finding)
- qc_certificate: PDF output (future)
- non_conformance_report: Linked NCR for fails

## Automation
- Checklist items auto-load from selected procedure
- NCR auto-created/linked on fail (major/critical)
- Validation for complete data and required photos

## Last Updated
2025-06-27
