# Repair Portal

Comprehensive documentation for the `repair_portal` Frappe app: modules, doctypes, dev flow, and conventions.

## Overview
- Domain app for instrument repair workflows: intake → inspection → setup → repair logging → QA → delivery.
- Built on Frappe/ERPNext; includes backend DocTypes with Python controllers and optional client scripts.

## Tech Stack
- Backend: Python 3.10, Frappe framework
- Frontend: Vanilla JS/Vue where needed, assets under `repair_portal/public`
- Tooling: Ruff, Flake8, Biome, ESLint, Pre-commit

## Installation
```bash
bench get-app local path/to/repair_portal  # or add as app in bench
bench --site <site> install-app repair_portal
bench --site <site> migrate
```

## Development
```bash
bench start                                 # run dev server
bench --site <site> clear-cache             # after schema/code changes
bench --site <site> run-tests --app repair_portal
npm run lint:backend && npm run lint:frontend
pre-commit run -a
```

## Project Structure
```
repair_portal/
  <module>/
    doctype/<doctype>/<doctype>.(py|js|json)
    report/, page/, config/, ...
public/ (assets)
```

## Modules and DocTypes
### Inspection
- Path: `repair_portal/inspection`
- DocTypes:
  - `instrument_inspection` (py,js)

### Intake
- Path: `repair_portal/intake`
- DocTypes:
  - `brand_mapping_rule` (py)
  - `clarinet_intake` (py,js)
  - `clarinet_intake_settings` (py)
  - `intake_accessory_item` (py)
  - `loaner_instrument` (py)
  - `loaner_return_check` (py)

### Instrument Setup
- Path: `repair_portal/instrument_setup`
- DocTypes:
  - `clarinet_initial_setup` (py,js)
  - `clarinet_pad_entry` (py)
  - `clarinet_pad_map` (py,js)
  - `clarinet_setup_log` (py,js)
  - `clarinet_setup_operation` (py)
  - `clarinet_setup_task` (py,js)
  - `clarinet_task_depends_on` (py,js)
  - `clarinet_template_task` (py,js)
  - `clarinet_template_task_depends_on` (py)
  - `setup_checklist_item` (py)
  - `setup_material_log` (py,js)
  - `setup_template` (py,js)

### QA
- Path: `repair_portal/qa`
- DocTypes:
  - `final_qa_checklist` (py)
  - `final_qa_checklist_item` (py)

### Repair Logging
- Path: `repair_portal/repair_logging`
- DocTypes:
  - `barcode_scan_entry` (py)
  - `diagnostic_metrics` (py)
  - `instrument_interaction_log` (py)
  - `key_measurement` (py)
  - `material_use_log` (py)
  - `pad_condition` (py)
  - `related_instrument_interaction` (py)
  - `repair_parts_used` (py)
  - `repair_task_log` (py)
  - `tenon_measurement` (py)
  - `tone_hole_inspection_record` (py,js)
  - `tool_usage_log` (py)
  - `visual_inspection` (py)
  - `warranty_modification_log` (py)

### Repair Portal
- Path: `repair_portal/repair_portal`
- DocTypes:
  - `pulse_update` (py)
  - `qa_checklist_item` (py)
  - `technician` (py,js)

### Service Planning
- Path: `repair_portal/service_planning`
- DocTypes:
  - `estimate_line_item` (py)
  - `repair_estimate` (py)
  - `service_plan` (py)
  - `service_task` (py)
  - `tasks` (py)

### Tools
- Path: `repair_portal/tools`
- DocTypes:
  - `tool` (py)
  - `tool_calibration_log` (py)

### Enhancements
- Path: `repair_portal/enhancements`
- DocTypes:
  - `customer_upgrade_request` (py)
  - `upgrade_option` (py)

### Instrument Profile
- Path: `repair_portal/instrument_profile`
- DocTypes:
  - `client_instrument_profile` (py,js)
  - `customer_external_work_log` (py,js)
  - `instrument` (py,js)
  - `instrument_accessory` (py)
  - `instrument_category` (py,js)
  - `instrument_condition_record` (py)
  - `instrument_model` (py,js)
  - `instrument_photo` (py)
  - `instrument_profile` (py,js)
  - `instrument_serial_number` (py,js)

### Repair
- Path: `repair_portal/repair`
- DocTypes:
  - `default_operations` (py,js)
  - `operation_template` (py)
  - `pulse_update` (py)
  - `repair_feedback` (py)
  - `repair_issue` (py)
  - `repair_order` (py,js)
  - `repair_request` (py,js)
  - `repair_task` (py)

### Lab
- Path: `repair_portal/lab`
- DocTypes:
  - `environment_log` (py)
  - `measurement_entry` (py)
  - `measurement_session` (py)

## Testing
- Uses Frappe test runner with `unittest`. Name tests `test_*.py` and scope fixtures to each test.
- Example sites are not required; tests create their own documents and clean up.

## Coding Standards
- Tabs for indentation; 110 char lines. Run `ruff format` / `ruff check` and Biome/ESLint for JS.
- Follow Frappe DocType conventions; do not edit generated JSON manually.

## Contributing
- Use Conventional Commits (e.g., `feat(instrument_setup): add task deps`).
- Open PRs with description, migration notes, and tests where applicable.

---

# Repair Portal - Comprehensive Project Documentation

Welcome to the **Repair Portal** application! This document provides a complete overview of the project, 
its architecture, technology stack, and business processes. It is designed to onboard new engineers 
who have zero prior knowledge of this codebase.

*Last updated: 2025-10-04*

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Codebase Architecture](#codebase-architecture)
4. [Key Business & Backend Logic](#key-business--backend-logic)
5. [Module Directory](#module-directory)
6. [Development Workflow](#development-workflow)
7. [Testing Strategy](#testing-strategy)
8. [Deployment & Installation](#deployment--installation)

---

## Project Overview

### Purpose

**Repair Portal** is a comprehensive instrument repair and customization management system built on the 
Frappe/ERPNext framework. The application is specifically designed for **Artisan Clarinets**, a professional 
clarinet repair, customization, and setup business.

### Business Problem

The application solves the following business challenges:

- **Instrument Intake Management**: Streamlines the process of receiving instruments for repair or setup
- **Repair Tracking**: Tracks repairs, tasks, and work orders from start to completion
- **Setup & Customization**: Manages complex clarinet setup procedures including pad mapping, key adjustments, and quality checks
- **Quality Assurance**: Implements comprehensive QA checklists and testing procedures
- **Customer Communication**: Provides customer portals for tracking repair status and instrument history
- **Inventory & Parts**: Tracks parts usage, material consumption, and inventory levels
- **Compliance & Documentation**: Maintains detailed logs, certificates, and audit trails
- **Technician Management**: Assigns tasks, tracks performance, and manages workload

### Core Functionality

The application provides end-to-end workflow management for:

1. **Instrument Intake**: Customer information, instrument details, initial assessment
2. **Inspection & Diagnosis**: Detailed instrument inspection and diagnostic procedures
3. **Setup & Configuration**: Comprehensive clarinet setup including pad mapping and adjustments
4. **Repair Work**: Task management, repair orders, and work logging
5. **Quality Control**: QA checklists, measurements, and final inspections
6. **Delivery & Certification**: Certificate generation, customer notifications, and delivery tracking

---

## Technology Stack

### Backend Framework

- **Frappe Framework v15**: Python-based full-stack web framework
- **ERPNext**: Business application platform built on Frappe
- **Python 3.10+**: Primary programming language
- **MariaDB/MySQL**: Database engine with InnoDB storage

### Frontend

- **Frappe Desk**: Web-based UI framework
- **JavaScript/ES6**: Client-side scripting
- **HTML/CSS**: Templates and styling
- **Jinja2**: Server-side templating

### Development Tools

- **Ruff**: Python linter and formatter
- **ESLint**: JavaScript linting
- **Biome**: Modern JavaScript formatter
- **Pre-commit**: Git hook framework for code quality
- **Pytest**: Testing framework

### Security & Compliance

- **Frappe Permissions**: Role-based access control (RBAC)
- **SQL Injection Protection**: Parameterized queries using frappe.qb
- **Audit Trails**: Comprehensive logging of all document changes
- **Consent Management**: GDPR-compliant customer consent tracking

---

## Codebase Architecture

### Architectural Pattern

The application follows a **Modular Monolith** architecture pattern:

- **Domain-Driven Design**: Organized by business modules (Intake, Inspection, Setup, Repair, QA)
- **MVC Pattern**: Model (DocTypes), View (Templates), Controller (Python classes)
- **Service Layer**: Reusable business logic in service modules
- **Event-Driven**: Document lifecycle hooks and event handlers

### Directory Structure

```
repair_portal/
├── repair_portal/              # Main application code
│   ├── customer/               # Customer & consent management
│   ├── intake/                 # Instrument intake workflows
│   ├── inspection/             # Instrument inspection processes
│   ├── instrument_setup/       # Setup & customization
│   ├── instrument_profile/     # Instrument master data
│   ├── player_profile/         # Player/musician profiles
│   ├── repair/                 # Repair orders & tasks
│   ├── repair_logging/         # Detailed repair logs
│   ├── qa/                     # Quality assurance
│   ├── service_planning/       # Service plans & estimates
│   ├── lab/                    # Measurement & testing
│   ├── tools/                  # Tool management
│   ├── stock/                  # Inventory management
│   ├── enhancements/           # Customer upgrades
│   ├── api/                    # REST API endpoints
│   ├── public/                 # Static assets
│   ├── patches/                # Database migrations
│   └── hooks.py                # Application hooks
├── scripts/                    # Utility scripts
├── documentation/              # Additional docs
├── REPORT/                     # Project reports
└── tests/                      # Test suites
```

### Module Organization

Each module follows a standard structure:

```
module_name/
├── doctype/                    # DocType definitions
│   └── doctype_name/
│       ├── doctype_name.json   # Schema definition
│       ├── doctype_name.py     # Controller logic
│       ├── doctype_name.js     # Client-side script
│       ├── test_*.py           # Unit tests
│       └── README.md           # Documentation
├── report/                     # Custom reports
├── page/                       # Custom pages
├── print_format/               # Print templates
└── web_form/                   # Public forms
```

---

## Key Business & Backend Logic

### Workflow Overview

The application implements a comprehensive workflow for instrument repair and customization:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌────────────┐
│   Intake    │────▶│  Inspection  │────▶│  Setup/Repair   │────▶│     QA     │
│ (Reception) │     │ (Diagnosis)  │     │   (Execution)   │     │  (Testing) │
└─────────────┘     └──────────────┘     └─────────────────┘     └────────────┘
                                                                         │
                                                                         ▼
                                                                  ┌──────────────┐
                                                                  │   Delivery   │
                                                                  │ (Completion) │
                                                                  └──────────────┘
```

### Core Business Processes

#### 1. Clarinet Intake

**DocType**: `Clarinet Intake`

- Captures customer and instrument information
- Records initial condition assessment
- Generates intake documentation
- Links to customer consent forms
- Assigns intake to technicians

#### 2. Instrument Inspection

**DocType**: `Instrument Inspection`

- Detailed visual inspection of instrument condition
- Tone hole measurements and pad condition assessment
- Key mechanism evaluation
- Photo documentation
- Generates inspection reports

#### 3. Clarinet Initial Setup

**DocType**: `Clarinet Initial Setup`

- Comprehensive setup project management
- Pad mapping and key adjustments
- Task dependencies and scheduling
- Material consumption tracking
- Progress monitoring and timelines
- Certificate generation upon completion

**Key Components:**
- **Setup Template**: Pre-defined setup procedures and checklists
- **Clarinet Pad Map**: Detailed pad configuration and measurements
- **Setup Tasks**: Granular task breakdown with dependencies
- **Material Logs**: Tracks all parts and materials used

#### 4. Repair Orders

**DocType**: `Repair Order`

- Manages repair work orders
- Links to repair tasks and operations
- Tracks labor hours and costs
- Material requisition and consumption
- Status updates and notifications

#### 5. Quality Assurance

**DocType**: `Final QA Checklist`

- Comprehensive quality checks before delivery
- Measurement verification
- Playability testing
- Visual inspection
- Approval workflow

### DocType Interactions

Key relationships between major doctypes:

- **Instrument Profile** ↔ All repair/setup activities (central master record)
- **Clarinet Intake** → **Instrument Inspection** (intake triggers inspection)
- **Clarinet Intake** → **Clarinet Initial Setup** (for new instrument setups)
- **Setup Template** → **Clarinet Initial Setup** (template instantiation)
- **Clarinet Pad Map** ↔ **Clarinet Initial Setup** (pad configuration)
- **Repair Order** ↔ **Repair Tasks** (work breakdown)
- **Repair Tasks** → **Repair Task Logs** (detailed work logging)
- **Final QA Checklist** → **Delivery** (quality gate)

### Automation & Business Rules

The application implements extensive automation:

1. **Auto-naming**: Sequential naming with prefixes (e.g., INT-2024-0001)
2. **Workflow State Transitions**: Automated status updates based on business rules
3. **Task Dependencies**: Automatic task scheduling based on dependencies
4. **Cost Calculations**: Auto-calculation of labor, materials, and total costs
5. **Notifications**: Email/SMS alerts for status changes and deadlines
6. **Document Generation**: Automated PDF certificates and reports
7. **Timeline Updates**: Automatic logging of all activities to timelines
8. **Profile Synchronization**: Instrument profiles auto-sync with related documents

---

## Module Directory

Below is a complete directory of all modules and their doctypes:

### Customer Management

**Path**: `repair_portal/customer/`

**DocTypes (11)**:

- **Consent Autofill Mapping** - [Documentation](repair_portal/customer/doctype/consent_autofill_mapping/README.md)
- **Consent Field Value** - [Documentation](repair_portal/customer/doctype/consent_field_value/README.md)
- **Consent Form** - [Documentation](repair_portal/customer/doctype/consent_form/README.md)
- **Consent Linked Source** - [Documentation](repair_portal/customer/doctype/consent_linked_source/README.md)
- **Consent Log Entry** - [Documentation](repair_portal/customer/doctype/consent_log_entry/README.md)
- **Consent Required Field** - [Documentation](repair_portal/customer/doctype/consent_required_field/README.md)
- **Consent Settings** - [Documentation](repair_portal/customer/doctype/consent_settings/README.md)
- **Consent Template** - [Documentation](repair_portal/customer/doctype/consent_template/README.md)
- **Customer Type** - [Documentation](repair_portal/customer/doctype/customer_type/README.md)
- **Instruments Owned** - [Documentation](repair_portal/player_profile/doctype/instruments_owned/README.md)
- **Linked Players** - [Documentation](repair_portal/customer/doctype/linked_players/README.md)

### Enhancements & Upgrades

**Path**: `repair_portal/enhancements/`

**DocTypes (2)**:

- **Customer Upgrade Request** - [Documentation](repair_portal/enhancements/doctype/customer_upgrade_request/README.md)
- **Upgrade Option** - [Documentation](repair_portal/enhancements/doctype/upgrade_option/README.md)

### Inspection

**Path**: `repair_portal/inspection/`

**DocTypes (1)**:

- **Instrument Inspection** - [Documentation](repair_portal/inspection/doctype/instrument_inspection/README.md)

### Instrument Profile

**Path**: `repair_portal/instrument_profile/`

**DocTypes (10)**:

- **Client Instrument Profile** - [Documentation](repair_portal/instrument_profile/doctype/client_instrument_profile/README.md)
- **Customer External Work Log** - [Documentation](repair_portal/instrument_profile/doctype/customer_external_work_log/README.md)
- **Instrument** - [Documentation](repair_portal/instrument_profile/doctype/instrument/README.md)
- **Instrument Accessory** - [Documentation](repair_portal/instrument_profile/doctype/instrument_accessory/README.md)
- **Instrument Category** - [Documentation](repair_portal/instrument_profile/doctype/instrument_category/README.md)
- **Instrument Condition Record** - [Documentation](repair_portal/instrument_profile/doctype/instrument_condition_record/README.md)
- **Instrument Model** - [Documentation](repair_portal/instrument_profile/doctype/instrument_model/README.md)
- **Instrument Photo** - [Documentation](repair_portal/instrument_profile/doctype/instrument_photo/README.md)
- **Instrument Profile** - [Documentation](repair_portal/instrument_profile/doctype/instrument_profile/README.md)
- **Instrument Serial Number** - [Documentation](repair_portal/instrument_profile/doctype/instrument_serial_number/README.md)

### Instrument Setup

**Path**: `repair_portal/instrument_setup/`

**DocTypes (11)**:

- **Clarinet Initial Setup** - [Documentation](repair_portal/instrument_setup/doctype/clarinet_initial_setup/README.md)
- **Clarinet Pad Entry** - [Documentation](repair_portal/instrument_setup/doctype/clarinet_pad_entry/README.md)
- **Clarinet Pad Map** - [Documentation](repair_portal/instrument_setup/doctype/clarinet_pad_map/README.md)
- **Clarinet Setup Log** - [Documentation](repair_portal/instrument_setup/doctype/clarinet_setup_log/README.md)
- **Clarinet Setup Operation** - [Documentation](repair_portal/instrument_setup/doctype/clarinet_setup_operation/README.md)
- **Clarinet Setup Task** - [Documentation](repair_portal/instrument_setup/doctype/clarinet_setup_task/README.md)
- **Clarinet Task Depends On** - [Documentation](repair_portal/instrument_setup/doctype/clarinet_task_depends_on/README.md)
- **Clarinet Template Task** - [Documentation](repair_portal/instrument_setup/doctype/clarinet_template_task/README.md)
- **Clarinet Template Task Depends On** - [Documentation](repair_portal/instrument_setup/doctype/clarinet_template_task_depends_on/README.md)
- **Setup Checklist Item** - [Documentation](repair_portal/instrument_setup/doctype/setup_checklist_item/README.md)
- **Setup Material Log** - [Documentation](repair_portal/instrument_setup/doctype/setup_material_log/README.md)
- **Setup Template** - [Documentation](repair_portal/instrument_setup/doctype/setup_template/README.md)

### Intake

**Path**: `repair_portal/intake/`

**DocTypes (5)**:

- **Brand Mapping Rule** - [Documentation](repair_portal/intake/doctype/brand_mapping_rule/README.md)
- **Clarinet Intake** - [Documentation](repair_portal/intake/doctype/clarinet_intake/README.md)
- **Intake Accessory Item** - [Documentation](repair_portal/intake/doctype/intake_accessory_item/README.md)
- **Loaner Instrument** - [Documentation](repair_portal/intake/doctype/loaner_instrument/README.md)
- **Loaner Return Check** - [Documentation](repair_portal/intake/doctype/loaner_return_check/README.md)

### Inventory

**Path**: `repair_portal/inventory/`

**DocTypes (2)**:

- **Pad Count Intake** - [Documentation](repair_portal/inventory/doctype/pad_count_intake/README.md)
- **Pad Count Log** - [Documentation](repair_portal/inventory/doctype/pad_count_log/README.md)

### Lab & Measurements

**Path**: `repair_portal/lab/`

**DocTypes (3)**:

- **Environment Log** - [Documentation](repair_portal/lab/doctype/environment_log/README.md)
- **Measurement Entry** - [Documentation](repair_portal/lab/doctype/measurement_entry/README.md)
- **Measurement Session** - [Documentation](repair_portal/lab/doctype/measurement_session/README.md)

### Player Profile

**Path**: `repair_portal/player_profile/`

**DocTypes (2)**:

- **Player Equipment Preference** - [Documentation](repair_portal/player_profile/doctype/player_equipment_preference/README.md)
- **Player Profile** - [Documentation](repair_portal/player_profile/doctype/player_profile/README.md)

### Quality Assurance

**Path**: `repair_portal/qa/`

**DocTypes (2)**:

- **Final Qa Checklist** - [Documentation](repair_portal/qa/doctype/final_qa_checklist/README.md)
- **Final Qa Checklist Item** - [Documentation](repair_portal/qa/doctype/final_qa_checklist_item/README.md)

### Repair

**Path**: `repair_portal/repair/`

**DocTypes (15)**:

- **Default Operations** - [Documentation](repair_portal/repair/doctype/default_operations/README.md)
- **Operation Template** - [Documentation](repair_portal/repair/doctype/operation_template/README.md)
- **Pulse Update** - [Documentation](repair_portal/repair/doctype/pulse_update/README.md)
- **Repair Actual Material** - [Documentation](repair_portal/repair/doctype/repair_actual_material/README.md)
- **Repair Feedback** - [Documentation](repair_portal/repair/doctype/repair_feedback/README.md)
- **Repair Issue** - [Documentation](repair_portal/repair/doctype/repair_issue/README.md)
- **Repair Order** - [Documentation](repair_portal/repair/doctype/repair_order/README.md)
- **Repair Planned Material** - [Documentation](repair_portal/repair/doctype/repair_planned_material/README.md)
- **Repair Quotation** - [Documentation](repair_portal/repair/doctype/repair_quotation/README.md)
- **Repair Quotation Item** - [Documentation](repair_portal/repair/doctype/repair_quotation_item/README.md)
- **Repair Related Document** - [Documentation](repair_portal/repair/doctype/repair_related_document/README.md)
- **Repair Request** - [Documentation](repair_portal/repair/doctype/repair_request/README.md)
- **Repair Task** - [Documentation](repair_portal/repair/doctype/repair_task/README.md)
- **Sla Policy** - [Documentation](repair_portal/repair/doctype/sla_policy/README.md)
- **Sla Policy Rule** - [Documentation](repair_portal/repair/doctype/sla_policy_rule/README.md)

### Repair Logging

**Path**: `repair_portal/repair_logging/`

**DocTypes (14)**:

- **Barcode Scan Entry** - [Documentation](repair_portal/repair_logging/doctype/barcode_scan_entry/README.md)
- **Diagnostic Metrics** - [Documentation](repair_portal/repair_logging/doctype/diagnostic_metrics/README.md)
- **Instrument Interaction Log** - [Documentation](repair_portal/repair_logging/doctype/instrument_interaction_log/README.md)
- **Key Measurement** - [Documentation](repair_portal/repair_logging/doctype/key_measurement/README.md)
- **Material Use Log** - [Documentation](repair_portal/repair_logging/doctype/material_use_log/README.md)
- **Pad Condition** - [Documentation](repair_portal/repair_logging/doctype/pad_condition/README.md)
- **Related Instrument Interaction** - [Documentation](repair_portal/repair_logging/doctype/related_instrument_interaction/README.md)
- **Repair Parts Used** - [Documentation](repair_portal/repair_logging/doctype/repair_parts_used/README.md)
- **Repair Task Log** - [Documentation](repair_portal/repair_logging/doctype/repair_task_log/README.md)
- **Tenon Measurement** - [Documentation](repair_portal/repair_logging/doctype/tenon_measurement/README.md)
- **Tone Hole Inspection Record** - [Documentation](repair_portal/repair_logging/doctype/tone_hole_inspection_record/README.md)
- **Tool Usage Log** - [Documentation](repair_portal/repair_logging/doctype/tool_usage_log/README.md)
- **Visual Inspection** - [Documentation](repair_portal/repair_logging/doctype/visual_inspection/README.md)
- **Warranty Modification Log** - [Documentation](repair_portal/repair_logging/doctype/warranty_modification_log/README.md)

### Repair Portal Core

**Path**: `repair_portal/repair_portal/`

**DocTypes (3)**:

- **Pulse Update** - [Documentation](repair_portal/repair_portal/doctype/pulse_update/README.md)
- **Qa Checklist Item** - [Documentation](repair_portal/repair_portal/doctype/qa_checklist_item/README.md)
- **Technician** - [Documentation](repair_portal/repair_portal/doctype/technician/README.md)

### Service Planning

**Path**: `repair_portal/service_planning/`

**DocTypes (5)**:

- **Estimate Line Item** - [Documentation](repair_portal/service_planning/doctype/estimate_line_item/README.md)
- **Repair Estimate** - [Documentation](repair_portal/service_planning/doctype/repair_estimate/README.md)
- **Service Plan** - [Documentation](repair_portal/service_planning/doctype/service_plan/README.md)
- **Service Task** - [Documentation](repair_portal/service_planning/doctype/service_task/README.md)
- **Tasks** - [Documentation](repair_portal/service_planning/doctype/tasks/README.md)

### Settings & Configuration

**Path**: `repair_portal/repair_portal_settings/`

**DocTypes (3)**:

- **Clarinet Intake Settings** - [Documentation](repair_portal/repair_portal_settings/doctype/clarinet_intake_settings/README.md)
- **Repair Portal Settings** - [Documentation](repair_portal/repair_portal_settings/doctype/repair_portal_settings/README.md)
- **Repair Settings** - [Documentation](repair_portal/repair_portal_settings/doctype/repair_settings/README.md)

### Stock & Inventory

**Path**: `repair_portal/stock/`

**DocTypes (2)**:

- **Delivery Note** - [Documentation](repair_portal/stock/doctype/delivery_note/README.md)
- **Stock Entry** - [Documentation](repair_portal/stock/doctype/stock_entry/README.md)

### Tools

**Path**: `repair_portal/tools/`

**DocTypes (2)**:

- **Tool** - [Documentation](repair_portal/tools/doctype/tool/README.md)
- **Tool Calibration Log** - [Documentation](repair_portal/tools/doctype/tool_calibration_log/README.md)

---



## Development Workflow

### Setup & Installation

```bash
# Clone the repository
bench get-app https://github.com/ArtisanClarinets/repair_portal

# Install on a site
bench --site <site-name> install-app repair_portal

# Run migrations
bench --site <site-name> migrate
```

### Development Commands

```bash
# Start development server
bench start

# Clear cache after code changes
bench --site <site-name> clear-cache

# Run linters
ruff check repair_portal/
ruff format repair_portal/

# Run JavaScript linters
npm run lint:frontend

# Run pre-commit checks
pre-commit run --all-files
```

### Coding Standards

- **Python**: Follow PEP 8, use tabs for indentation, 110 character line limit
- **JavaScript**: Use ESLint configuration, modern ES6+ syntax
- **Frappe Conventions**: Use Frappe's Document API, avoid raw SQL
- **Security**: Always use parameterized queries, check permissions
- **Documentation**: Update README.md files when adding/modifying doctypes

---

## Testing Strategy

### Test Structure

Each doctype should have corresponding tests:

```python
# Example: test_clarinet_intake.py
import frappe
from frappe.tests.utils import FrappeTestCase

class TestClarinetIntake(FrappeTestCase):
    def test_creation(self):
        # Test document creation
        pass
    
    def test_validation(self):
        # Test validation logic
        pass
```

### Running Tests

```bash
# Run all tests
bench --site <site-name> run-tests --app repair_portal

# Run specific test
bench --site <site-name> run-tests --app repair_portal --module clarinet_intake
```

---

## Deployment & Installation

### Production Installation

```bash
# On production bench
bench get-app repair_portal
bench --site erp.artisanclarinets.com install-app repair_portal
bench --site erp.artisanclarinets.com migrate
bench restart
```

### Environment Configuration

Set up the following in `site_config.json`:

```json
{
  "db_name": "your_database",
  "db_password": "secure_password",
  "developer_mode": 0,
  "maintenance_mode": 0
}
```

### Database Migrations

All migrations are in `repair_portal/patches/` directory. They run automatically during `bench migrate`.

---

## Additional Resources

- **Frappe Framework Documentation**: https://frappeframework.com/docs
- **ERPNext Documentation**: https://docs.erpnext.com
- **Project CHANGELOG**: See `CHANGELOG.md` for version history
- **AGENTS.md**: Developer agent instructions and workflows

## Maintainers

- **Lead Engineer**: Dylan Thompson (Artisan Clarinets)
- **Contact**: info@artisanclarinets.com
- **Repository**: https://github.com/ArtisanClarinets/repair_portal

---

*This documentation was auto-generated on 2025-10-04 and provides 
Fortune-500 quality onboarding materials for new engineers, auditors, and stakeholders.*
