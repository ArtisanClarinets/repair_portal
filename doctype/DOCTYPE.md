# DocType Overlap Audit

## Material & Inventory Line Items
- **Setup Material Log** and **Intake Accessory Item** define the same child-table schema of `item_code`, `description`, `qty`, `uom`, `rate`, and `amount`, differing only in optional metadata flags.【F:repair_portal/instrument_setup/doctype/setup_material_log/setup_material_log.json†L1-L76】【F:repair_portal/intake/doctype/intake_accessory_item/intake_accessory_item.json†L1-L91】 
- **Planned Material** and **Repair Planned Material** both model planned consumption with near-identical fields; only the repair variant adds a `notes` column while the generic table already covers warehouse, vendor, and reservation data.【F:repair_portal/repair/doctype/planned_material/planned_material.json†L1-L93】【F:repair_portal/repair/doctype/repair_planned_material/repair_planned_material.json†L1-L68】 
- **Actual Material**, **Repair Actual Material**, **Repair Parts Used**, and **Material Use Log** each capture the same core data (item, quantity, UOM, rate/amount, warehouse/reference) for realized usage, introducing only cosmetic differences in field names or optional links.【F:repair_portal/repair/doctype/actual_material/actual_material.json†L1-L63】【F:repair_portal/repair/doctype/repair_actual_material/repair_actual_material.json†L1-L80】【F:repair_portal/repair_logging/doctype/repair_parts_used/repair_parts_used.json†L1-L83】【F:repair_portal/repair_logging/doctype/material_use_log/material_use_log.json†L1-L77】

**Recommendation**
1. Promote a single reusable child DocType (e.g., `Material Line Item`) with optional context fields (warehouse, valuation, source document) and migrate existing parents to reference it. 
2. Consolidate planned vs actual distinctions via a status flag instead of separate doctypes; store scenario-specific metadata (e.g., template vs live usage) in parent documents. 
3. Use ERPNext stock tables (e.g., Stock Entry Detail) where possible to remove custom duplication, and expose context fields through custom scripts if needed.

## Estimation, Quotation & Upsell Items
- **Repair Quotation Item** and **Estimate Line Item** both represent labor/part lines with quantity, hours, rate, and amount columns, differing mainly in naming and a few contextual flags.【F:repair_portal/repair/doctype/repair_quotation_item/repair_quotation_item.json†L1-L93】【F:repair_portal/service_planning/doctype/estimate_line_item/estimate_line_item.json†L1-L106】 
- **Class Upsell** and **Estimate Upsell** are the same upsell child table with the latter adding a boolean `accepted` flag; both link to `Item` and capture price/description.【F:repair_portal/repair/doctype/class_upsell/class_upsell.json†L1-L34】【F:repair_portal/service_planning/doctype/estimate_upsell/estimate_upsell.json†L1-L41】 
- The parent doctypes **Repair Quotation** and **Repair Estimate** track similar customer/instrument references, totals, and line tables, effectively duplicating the estimate workflow.【F:repair_portal/repair/doctype/repair_quotation/repair_quotation.json†L1-L120】【F:repair_portal/service_planning/doctype/repair_estimate/repair_estimate.json†L1-L90】

**Recommendation**
1. Standardize on a single quoting DocType (e.g., extend `Repair Estimate`) and expose additional acceptance metadata there; deprecate redundant parents and child tables after migrating data. 
2. Replace the duplicated upsell child tables with one `Upsell Option` table containing an optional `accepted` flag; update downstream reports to filter by context. 
3. Introduce a unified pricing API/service that maps estimate lines to execution tasks/materials, ensuring downstream documents (orders, stock movements) consume the same schema.

## Task & Checklist Management
- **Repair Task**, **Service Task**, and **Clarinet Setup Task** all track assigned users, status, scheduling fields, and completion metrics, with the setup variant adding Gantt/dependency metadata.【F:repair_portal/repair/doctype/repair_task/repair_task.json†L1-L26】【F:repair_portal/service_planning/doctype/service_task/service_task.json†L1-L27】【F:repair_portal/instrument_setup/doctype/clarinet_setup_task/clarinet_setup_task.json†L1-L200】 
- Checklist child tables (**QA Checklist Item**, **Final QA Checklist Item**, and **Setup Checklist Item**) share the same boolean outcome plus notes, differing only in label names.【F:repair_portal/qa/doctype/qa_checklist_item/qa_checklist_item.json†L1-L47】【F:repair_portal/qa/doctype/final_qa_checklist_item/final_qa_checklist_item.json†L1-L56】【F:repair_portal/instrument_setup/doctype/setup_checklist_item/setup_checklist_item.json†L1-L46】 
- Additional child task tables (e.g., `Tasks` under Service Planning) repeat minimal text/date fields for TODO tracking.【F:repair_portal/service_planning/doctype/tasks/tasks.json†L1-L22】

**Recommendation**
1. Create a module-agnostic `Service Task` DocType with feature flags for dependencies, workflow state, and SLA to cover all scenarios; migrate existing doctypes to either extend or reference this base through DocType inheritance/customization. 
2. Merge checklist items into one reusable child DocType (`Checklist Line`) parameterized by checklist type; store context (QA vs Setup) on the parent or via a `category` Select. 
3. Align workflow states, permissions, and dashboards around the unified task model to avoid divergent status vocabularies.

## Inspection & Measurement Logging
- **Instrument Inspection** already captures serial-linked inspection metadata, tone-hole observations, pad notes, and accessory logs; the **Visual Inspection** child table redefines the same component/status/photo schema in isolation.【F:repair_portal/inspection/doctype/instrument_inspection/instrument_inspection.json†L1-L200】【F:repair_portal/repair_logging/doctype/visual_inspection/visual_inspection.json†L1-L64】 
- Specialized tone-hole and pad tracking (**Tone Hole Inspection Record**, **Key Measurement**, **Tenon Measurement**) overlap with `Instrument Inspection` fields and the lab measurement tables, duplicating numeric and status capture patterns.【F:repair_portal/repair_logging/doctype/tone_hole_inspection_record/tone_hole_inspection_record.json†L1-L46】【F:repair_portal/repair_logging/doctype/key_measurement/key_measurement.json†L1-L54】【F:repair_portal/repair_logging/doctype/tenon_measurement/tenon_measurement.json†L1-L62】 
- Lab doctypes (**Measurement Entry** and **Measurement Session**) provide a structured parent/child pattern that could host the same data currently scattered across repair logging tables.【F:repair_portal/lab/doctype/measurement_entry/measurement_entry.json†L1-L45】【F:repair_portal/lab/doctype/measurement_session/measurement_session.json†L1-L85】

**Recommendation**
1. Expand `Instrument Inspection` (or a new `Inspection Finding` child) to include component-level observations, replacing bespoke visual/tone-hole tables. 
2. Reuse the Lab measurement session architecture for all numeric diagnostics, adding measurement-type metadata instead of proliferating distinct doctypes. 
3. Provide migration scripts that consolidate historical records into the unified structures and add source tags for provenance.

## Activity & Communication Logs
- **Clarinet Setup Log**, **Pulse Update**, **Instrument Interaction Log**, and **Repair Task Log** all store free-form notes tied to a customer/instrument, timestamp, and author, each targeting a different workflow stage.【F:repair_portal/instrument_setup/doctype/clarinet_setup_log/clarinet_setup_log.json†L1-L108】【F:repair_portal/repair/doctype/pulse_update/pulse_update.json†L1-L73】【F:repair_portal/repair_logging/doctype/instrument_interaction_log/instrument_interaction_log.json†L1-L67】【F:repair_portal/repair_logging/doctype/repair_task_log/repair_task_log.json†L1-L46】

**Recommendation**
1. Replace disparate log doctypes with a single `Instrument Activity Log` child table that records activity type, reference doc, timestamp, author, and narrative. 
2. Feed updates from tasks, inspections, and communications into this unified log via hooks, improving traceability and simplifying customer portal feeds. 
3. Configure role-based filters/view templates instead of separate doctypes to present context-specific timelines.

## Consolidation Roadmap
1. **Assessment & Design**: Inventory parent doctypes that reference the duplicated children and design canonical schemas (Material Line Item, Checklist Line, Inspection Finding, Activity Log). Engage stakeholders to confirm required context fields. 
2. **Schema Refactor**: Introduce new canonical doctypes, add compatibility columns, and update links/controllers to point to the shared tables. Ensure backward compatibility via patches that migrate data and preserve permissions. 
3. **Data Migration**: Write idempotent patch scripts to move legacy records into the unified doctypes, recording source DocType and name for audit history. 
4. **Deprecation & Cleanup**: After successful migration, remove redundant doctypes and update frontend forms/reports to consume the new schema. Archive retired doctypes via export before deletion. 
5. **Governance**: Document reusable doctypes and add lint checks preventing new module-specific clones; enforce via code review templates and automated schema guard rules.
