# Repair Portal

## Module: Repair Order

### DocTypes Implemented
- **Repair Order**: Central workflow object for repair lifecycle
- **Repair Test Result**: Child table capturing specific diagnostic results
- **Common Notes**: Shared notes child table used across documents

### Workflows
- **Repair Order Workflow**: 
  - Draft → In Progress → QA → Ready for Pickup → Closed

### Server Logic
- **repair_parts_stock_entry.py**: Auto-generates Stock Entry on repair part log
- **repair_order_invoice_auto.py**: Creates Sales Invoice upon Repair Order submission

### UI & Navigation
- Custom Workspace: `Repair Orders`

### Next Steps
- Add unit tests
- Add CI hooks via GitHub Actions

*Last updated: 2025-06-26*