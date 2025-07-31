# Controller Review

This document will contain a comprehensive review of all controllers in the `repair_portal` application. Each section will detail the controller's location, purpose, main endpoints, and any notable implementation details or recommendations.

---

[repair_portal/api/technician_dashboard.py]
Purpose: API endpoint for technician dashboard, focused on Repair Orders.
Main Endpoint: `get_dashboard_data(technician=None)`
- Fetches KPIs, assigned repairs, and recent activity for a technician.
- Enforces role-based access (Technician role required).
- Uses SQL queries and Frappe ORM for data aggregation.
Recommendations: Consider pagination for assigned repairs, and optimize SQL for large datasets.

[repair_portal/api/client_portal.py]
Purpose: Secure API endpoints for client portal dashboard.
Main Endpoints:
- `get_my_instruments()`: Returns instruments linked to the logged-in user.
- `get_my_repairs()`: Returns recent Repair Orders for user's instruments.
- Uses Frappe ORM and role-based access.
Recommendations: Add error handling for missing linked users, and consider caching for frequent queries.

[repair_portal/api/customer.py]
Purpose: Securely retrieve client profile data.
Main Function: `get_customer(client_id: str)`
- Returns public profile fields for a given Customer.
- Checks read permission and handles errors robustly.
Recommendations: Expose as a whitelisted endpoint if needed, and validate client_id input.

[repair_portal/api/intake_dashboard.py]
Purpose: API endpoints for Intake Dashboard.
Main Endpoints:
- `get_intake_counts()`: Returns counts of intakes by workflow state.
- `get_recent_intakes()`: Returns recent intake records.
- Uses Frappe ORM for queries.
Recommendations: Add filtering options for recent intakes, and consider performance for large datasets.

[repair_portal/api/clarinet_utils.py]
Purpose: Utility functions for clarinet-related operations.
Main Functions:
- `get_instrument_profile(serial_no)`: Fetches instrument profile by serial number, throws if not found.
- `mark_instrument_archived(instrument_name)`: Archives an instrument profile.
Recommendations: Add whitelisting if needed, and improve error messages for user-facing endpoints.

[repair_portal/api/__init__.py]
Purpose: Module initializer (currently empty).
Recommendations: No action needed unless shared imports or setup logic required.

[repair_portal/customer/dashboard/customer_dashboard/customer_dashboard.py]
Purpose: Provides dashboard data for customers, aggregating transactions and charts related to players, instruments, repairs, lab results, and QA reports.
Main Function: `get_data()`
- Returns dashboard configuration including fieldname, transactions, and charts.
- Integrates with Player Profile, Instrument Profile, Repair Log, Setup Log, Leak Test, Intonation Session, and Instrument Inspection.
Recommendations: Consider dynamic chart data population and user-specific filtering for improved UX.

[repair_portal/customer/doctype/consent_field_value/consent_field_value.py]
Purpose: Child table to store each consent form's field values.
Class: `ConsentFieldValue(Document)`
- Stores field label, type, and entered value for each filled consent.
Recommendations: Add validation for field types and required values if needed.

[repair_portal/customer/doctype/consent_field_value/__init__.py]
Purpose: Module initializer for Consent Field Value child table.
Recommendations: No action needed unless shared imports or setup logic required.

[repair_portal/customer/doctype/consent_form/consent_form.py]
Purpose: Backend controller for Consent Form; generates, validates, and renders filled agreements.
Class: `ConsentForm(Document)`
- Validates required fields, renders agreement using Consent Template, auto-fills company info and date, and handles signature rendering.
Recommendations: Ensure robust error handling for template and field value mismatches; consider exposing render_agreement as a utility.

[repair_portal/customer/doctype/consent_form/__init__.py]
Purpose: Module initializer for Consent Form.
Recommendations: No action needed unless shared imports or setup logic required.

[repair_portal/customer/doctype/consent_log/consent_log.py]
Purpose: Enforces required fields for Consent Log child table.
Class: `ConsentLog(Document)`
- Validates that date and type are provided.
Recommendations: Add more granular validation for consent types if business logic requires.

[repair_portal/customer/doctype/consent_log_entry/consent_log_entry.py]
Purpose: Enforces required fields for Consent Log Entry child table.
Class: `ConsentLogEntry(Document)`
- Validates that entry date and method are filled before saving.
Recommendations: Add validation for method types and entry date format if needed.

[repair_portal/customer/doctype/consent_required_field/consent_required_field.py]
Purpose: Child table for required fields in Consent Template.
Class: `ConsentRequiredField(Document)`
- Lists dynamic required fields in Consent Templates.
Recommendations: Add validation for field uniqueness and type if needed.

[repair_portal/customer/doctype/consent_required_field/__init__.py]
Purpose: Module initializer for Consent Required Field child table.
Recommendations: No action needed unless shared imports or setup logic required.

[repair_portal/customer/doctype/consent_template/consent_template.py]
Purpose: Backend controller for Consent Template DocType.
Class: `ConsentTemplate(Document)`
- Defines consent type, content, active status, title, validity, and version.
Recommendations: Ensure content is properly templated and versioned; add validation for active status and validity dates.

[repair_portal/customer/doctype/consent_template/__init__.py]
Purpose: Module initializer for Consent Template.
Recommendations: No action needed unless shared imports or setup logic required.

[repair_portal/customer/doctype/consent_template/test_consent_template.py]
Purpose: Unit test for Consent Template DocType.
Class: `TestConsentTemplate(FrappeTestCase)`
- Placeholder for automated tests.
Recommendations: Add tests for template rendering, field validation, and versioning logic.

[repair_portal/customer/doctype/customer_consent/customer_consent_form.py]
Purpose: Handles legal consent authorization, including customer info, instrument details, and digital signature capture.
Class: `CustomerConsentForm(Document)`
- Stores consent form data and signature.
Recommendations: Add validation for required fields and signature format.

[repair_portal/customer/doctype/customer_consent/customer_consent.py]
Purpose: Holds completed customer consent forms, filled values, signature, and locked HTML.
Class: `CustomerConsent(Document)`
- Generates unique name, renders HTML consent, attaches signature image, and logs errors.
Recommendations: Ensure robust error handling and field mapping; consider exposing rendering logic for reuse.

[repair_portal/customer/doctype/customer_consent/__init__.py]
Purpose: Module initializer for Customer Consent.
Recommendations: No action needed unless shared imports or setup logic required.

[repair_portal/customer/doctype/customer_type/customer_type.py]
Purpose: Enforces single-default logic for Customer Types.
Class: `CustomerType(Document)`
- Ensures only one profile type is marked as default, deduplicates via SQL update.
Recommendations: Add validation for type uniqueness and error handling for SQL failures.

[repair_portal/customer/doctype/customer_type/__init__.py]
Purpose: Module initializer for Customer Type.
Recommendations: No action needed unless shared imports or setup logic required.

[repair_portal/customer/doctype/instruments_owned/instruments_owned.py]
Purpose: Refactored child table to support Customer linkage in ERPNext-native architecture.
Class: `InstrumentsOwned(Document)`
- Validates that customer link is present for each entry.
Recommendations: Add validation for serial number format and uniqueness.

[repair_portal/customer/doctype/linked_players/__init__.py]
Purpose: Module initializer for Linked Players child table.
Recommendations: No action needed unless shared imports or setup logic required.

[repair_portal/customer/doctype/linked_players/linked_players.py]
Purpose: Server-side controller for Linked Players child doctype.
Class: `LinkedPlayers(Document)`
- Validates existence and status of linked Person and Player Profile.
- Prevents duplicate links and enforces single primary profile per parent.
- Normalizes date fields and logs errors for debugging.
Recommendations: Add more granular validation for relationship types and improve error messages for user-facing exceptions.

[repair_portal/customer/page/client_portal/__init__.py]
Purpose: Module initializer for client portal page.
Recommendations: No action needed unless shared imports or setup logic required.

[repair_portal/enhancements/doctype/customer_upgrade_request/customer_upgrade_request.py]
Purpose: Handles customer upgrade requests, validates serial numbers, and logs upgrade interactions in Instrument Tracker.
Class: `CustomerUpgradeRequest(Document)`
- On submit, checks serial number existence and appends upgrade interaction log.
Recommendations: Add error handling for missing or invalid serial numbers; consider logging failed attempts for audit.

[repair_portal/enhancements/doctype/upgrade_option/upgrade_option.py]
Purpose: Defines upgrade options for customer requests.
Class: `UpgradeOption(Document)`
- Stores upgrade option details.
Recommendations: Add validation for option uniqueness and required fields.

[repair_portal/enhancements/report/top_upgrade_requests/top_upgrade_requests.py]
Purpose: Report showing most requested upgrade types.
Function: `execute(filters=None)`
- Aggregates upgrade requests and returns top 10 upgrade descriptions.
Recommendations: Add filtering by date range and customer for more granular insights.

[repair_portal/enhancements/report/upgrade_conversion_rates/upgrade_conversion_rates.py]
Purpose: Report aggregating upgrade request statuses for conversion insights.
Function: `execute(filters=None)`
- Groups requests by customer and status.
Recommendations: Add filtering by upgrade type and time period; consider visualizing conversion rates.

[repair_portal/inspection/doctype/instrument_inspection/__init__.py]
Purpose: Module initializer for Instrument Inspection DocType.
Recommendations: No action needed unless shared imports or setup logic required.

[repair_portal/inspection/doctype/instrument_inspection/instrument_inspection.py]
Purpose: Controller for Instrument Inspection DocType; handles validation, automation, and exception logging for all inspection scenarios.
Class: `InstrumentInspection(Document)`
- Validates unique serial numbers, required fields, and business rules for inspection types.
- On submit, syncs inspection specs to Instrument Profile.
Recommendations: Add child table mappings for photos/media; improve error handling and logging.

[repair_portal/inspection/doctype/instrument_inspection/test_instrument_inspection.py]
Purpose: Comprehensive test suite for Instrument Inspection DocType.
Class: `TestInstrumentInspection(FrappeTestCase)`
- Tests validation, business logic, and model integrity for all inspection types.
Recommendations: Expand tests for child table persistence and edge cases.

[repair_portal/inspection/page/technician_dashboard/__init__.py]
Purpose: Module initializer for technician dashboard page.
Recommendations: No action needed unless shared imports or setup logic required.

[repair_portal/instrument_profile/doctype/client_instrument_profile/client_instrument_profile.py]
Purpose: Server-side logic for client-created instrument profiles.
Class: `ClientInstrumentProfile(Document)`
- Validates technician notes on rejection; updates Instrument Profile on approval.
Recommendations: Add validation for required fields and improve error messages for user-facing actions.

[repair_portal/instrument_profile/doctype/customer_external_work_log/customer_external_work_log.py]
Purpose: Controller for customer-submitted repair history logs.
Class: `CustomerExternalWorkLog(Document)`
- Stores external work log entries submitted by customers.
Recommendations: Add validation for required fields and date formats.

[repair_portal/instrument_profile/doctype/external_work_logs/external_work_logs.py]
Purpose: Controller for External Work Logs child table.
Class: `ExternalWorkLogs(Document)`
- Stores external work log details for instruments.
Recommendations: Add validation for log type and required fields.

[repair_portal/instrument_profile/doctype/instrument_accessory/instrument_accessory.py]
Purpose: Child table for Instrument Accessories (paired, acquired/removed, description).
Class: `InstrumentAccessory(Document)`
- Tracks accessories on instrument profiles.
Recommendations: Add validation for accessory type and acquisition/removal dates.

[repair_portal/instrument_profile/doctype/instrument_category/instrument_category.py]
Purpose: Minimal controller for Instrument Category DocType (category master for instruments).
Class: `InstrumentCategory(Document)`
- Stores instrument category details.
Recommendations: Add validation for category uniqueness and active status.

[repair_portal/instrument_profile/doctype/instrument_condition_record/instrument_condition_record.py]
Purpose: Controller for Instrument Condition Record DocType; manages validation, workflow state transitions, and business logic.
Class: `InstrumentConditionRecord(Document)`
- Validates date, notes, and workflow transitions; updates instrument status and notifies inspection team.
Recommendations: Add more granular workflow state validation and improve notification logic.

[repair_portal/instrument_profile/doctype/instrument/instrument.py]
Purpose: Instrument DocType controller for validation, naming, and business logic for musical instrument records.
Class: `Instrument(Document)`
- Validates duplicate serial numbers, instrument category, and generates custom instrument_id.
Recommendations: Add validation for year_of_manufacture and improve error handling for autoname logic.

[repair_portal/instrument_profile/doctype/instrument_media/instrument_media.py]
Purpose: Manage media files associated with instrument profiles.
Class: `InstrumentMedia(Document)`
- Handles file uploads, deletions, and retrievals for instrument media.
Recommendations: Add validation for file types and media metadata.

[repair_portal/instrument_profile/doctype/instrument_model/instrument_model.py]
Purpose: Controller for Instrument Model DocType.
Class: `InstrumentModel(Document)`
- Stores instrument model details and links to category and brand.
Recommendations: Add validation for model uniqueness and required fields.

[repair_portal/instrument_profile/doctype/instrument_photo/instrument_photo.py]
Purpose: Child table to store all photo/image records linked to an instrument's lifecycle.
Class: `InstrumentPhoto(Document)`
- Used for photo attachments on Instrument, Inspection, and Profile doctypes.
Recommendations: Add validation for image type and required metadata.

[repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py]
Purpose: Handles ERPNext Serial No syncing for instruments, warranty expiration sync, and links repair, inspection, and related logs.
Class: `InstrumentProfile(Document)`
- Syncs Serial No, warranty expiration, and auto-populates related logs as child tables.
Recommendations: Add error handling for failed syncs and improve audit trail for linked records.

[repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.py]
Purpose: Complete Clarinet Initial Setup lifecycle; enforces intake link, checklist, and automation for setup operations and material usage.
Class: `ClarinetInitialSetup(Document)`
- Validates intake reference, checklist, and material stock; automates technician assignment and PDF certificate generation.
Recommendations: Add error handling for PDF generation and improve automation for setup operations.

[repair_portal/instrument_setup/doctype/clarinet_pad_entry/clarinet_pad_entry.py]
Purpose: Represents a single pad definition for top/bottom joint pad entries.
Class: `ClarinetPadEntry(Document)`
- Describes pad position, type, and open/closed status for clarinet pads.
Recommendations: Add validation for pad position and type.

[repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.py]
Purpose: Auto-populates pad layout template for French-style clarinets using instrument category; exposes method for client trigger.
Class: `ClarinetPadMap(Document)`
- Auto-populates standard pad names for top/bottom joints; exposes whitelisted method for client-side triggers.
Recommendations: Add error handling for pad population and improve category detection logic.

[repair_portal/instrument_setup/doctype/clarinet_setup_log/clarinet_setup_log.py]
Purpose: Controller for Clarinet Setup Log; supports documentation and auditing setup actions.
Class: `ClarinetSetupLog(Document)`
- Stores setup log entries for clarinet setups.
Recommendations: Add validation for required fields and setup dates.

[repair_portal/instrument_setup/doctype/clarinet_setup_operation/clarinet_setup_operation.py]
Purpose: Tracks manual service tasks by section and type for clarinet setup operations.
Class: `ClarinetSetupOperation(Document)`
- Stores setup operation details for clarinet setups.
Recommendations: Add validation for operation type and completion status.

[repair_portal/instrument_setup/doctype/inspection_finding/inspection_finding.py]
Purpose: Tracks inspection issues and recommended actions for clarinet setups.
Class: `InspectionFinding(Document)`
- Stores inspection findings, actions required, and severity.
Recommendations: Add validation for issue type and severity.

[repair_portal/instrument_setup/doctype/setup_checklist_item/setup_checklist_item.py]
Purpose: Setup Checklist Item for technician task tracking in Clarinet Initial Setup.
Class: `SetupChecklistItem(Document)`
- Stores checklist items for setup tasks.
Recommendations: Add validation for mandatory status and completion.

[repair_portal/instrument_setup/doctype/setup_template/setup_template.py]
Purpose: Auto-creates Clarinet Pad Map on Setup Template save.
Class: `SetupTemplate(Document)`
- Validates pad map existence and auto-creates if missing.
Recommendations: Add error handling for pad map creation and improve template validation.

[repair_portal/instrument_setup/report/parts_consumption/parts_consumption.py]
Purpose: Report for total quantity of parts used in clarinet setups.
Function: `execute(filters=None)`
- Aggregates material usage by item code and quantity.
Recommendations: Add filtering by date range and technician.

[repair_portal/instrument_setup/report/technician_performance/technician_performance.py]
Purpose: Report for technician performance in clarinet setups.
Function: `execute(filters=None)`
- Aggregates setups, pass rate, and average hours by technician.
Recommendations: Add filtering by time period and setup type.

[repair_portal/intake/doctype/brand_mapping_rule/brand_mapping_rule.py]
Purpose: Defines brand mapping rules for instrument profiles.
Class: `BrandMappingRule(Document)`
- Validates brand name, instrument category, and uniqueness of mapping.
Recommendations: Add error handling for duplicate mappings and improve validation logic.

[repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py]
Purpose: Ensures all intake types auto-create Instrument, Item, Serial No, Instrument Inspection, and Initial Setup as needed.
Class: `ClarinetIntake(Document)`
- Automates creation of related records and enforces mandatory fields by intake type.
Recommendations: Add error handling for failed automations and improve intake validation.

[repair_portal/intake/doctype/clarinet_intake/clarinet_intake_timeline.py]
Purpose: Logs each auto-generated child record in the intake timeline after Clarinet Intake creation.
Function: `add_timeline_entries(doc, method)`
- Adds info comments with links to created records.
Recommendations: Add error handling for missing records and improve logging granularity.

[repair_portal/intake/doctype/clarinet_intake_settings/clarinet_intake_settings.py]
Purpose: Backend controller for Clarinet Intake Settings; provides utility for business logic to fetch settings.
Class: `ClarinetIntakeSettings(Document)`
- Stores intake settings and provides utility function for fetching settings as dict.
Recommendations: Add validation for required settings fields.

[repair_portal/intake/doctype/intake_accessory_item/intake_accessory_item.py]
Purpose: Validation and lifecycle hooks for Accessories Checklist entries.
Class: `IntakeAccessoryItem(Document)`
- Validates accessory description, quantity, and notes.
Recommendations: Add error handling for invalid accessory types and improve quantity validation.

[repair_portal/intake/doctype/intake_checklist_item/intake_checklist_item.py]
Purpose: Defines checklist items to be reviewed during instrument intake process.
Class: `IntakeChecklistItem(Document)`
- Stores checklist items for intake review.
Recommendations: Add validation for mandatory status and completion.

[repair_portal/intake/doctype/loaner_instrument/loaner_instrument.py]
Purpose: Adds auto-PDF generation and digital agreement signing for loaner issuance.
Class: `LoanerInstrument(Document)`
- Generates, attaches, and notifies for loaner agreement PDF; logs errors for audit.
Recommendations: Add error handling for PDF generation and improve agreement template logic.

[repair_portal/intake/doctype/loaner_return_check/loaner_return_check.py]
Purpose: Manages post-save and validation logic for loaner return checks.
Class: `LoanerReturnCheck(Document)`
- Validates condition notes when damage is flagged.
Recommendations: Add validation for return dates and improve error messages.

[repair_portal/intake/report/deposit_balance_aging/deposit_balance_aging.py]
Purpose: Script report for deposit balance aging by customer.
Function: `execute(filters=None)`
- Aggregates deposit balances by customer.
Recommendations: Add filtering by date range and customer type.

[repair_portal/intake/report/followup_compliance/followup_compliance.py]
Purpose: Report showing compliance rate of Intake Follow-ups, with status and date-range filters.
Function: `execute(filters=None)`
- Returns compliance data and columns for Frappe report engine.
Recommendations: Add more granular filtering and improve logging for report queries.

[repair_portal/lab/doctype/environment_log/environment_log.py]
Purpose: Validation and lifecycle hooks for Environment Log entries.
Class: `EnvironmentLog(Document)`
- Stores environment log entries for lab conditions.
Recommendations: Add validation for required fields and log types.

[repair_portal/lab/doctype/impedance_peak/impedance_peak.py]
Purpose: Child table for impedance peak data.
Class: `ImpedancePeak(Document)`
- Stores impedance peak readings for lab analysis.
Recommendations: Add validation for peak value and measurement date.

[repair_portal/lab/doctype/impedance_snapshot/impedance_snapshot.py]
Purpose: Parent DocType to store impedance sweep snapshots.
Class: `ImpedanceSnapshot(Document)`
- Stores impedance sweep data for instruments.
Recommendations: Add validation for snapshot completeness and instrument linkage.

[repair_portal/lab/doctype/instrument_wellness_score/instrument_wellness_score.py]
Purpose: Automatically compute an instrument's wellness score from lab data.
Class: `InstrumentWellnessScore(Document)`
- Calculates intonation, impedance, leak, and tone scores; computes weighted average.
Recommendations: Add error handling for missing lab data and improve score calculation logic.

[repair_portal/lab/doctype/intonation_note/intonation_note.py]
Purpose: Child table for individual intonation readings.
Class: `IntonationNote(Document)`
- Stores intonation readings for lab sessions.
Recommendations: Add validation for note value and reading accuracy.

[repair_portal/lab/doctype/intonation_session/intonation_session.py]
Purpose: Parent DocType for smart intonation sessions.
Class: `IntonationSession(Document)`
- Stores intonation session data and associated notes.
Recommendations: Add validation for session type and instrument linkage.

[repair_portal/lab/doctype/lab_intonation_session/lab_intonation_session.py]
Purpose: Stores intonation measurement sessions and associated acoustic analysis.
Class: `LabIntonationSession(Document)`
- Validates instrument selection and logs submission events.
Recommendations: Add error handling for acoustic analysis and improve session validation.

[repair_portal/lab/doctype/leak_reading/leak_reading.py]
Purpose: Child table for leak test readings.
Class: `LeakReading(Document)`
- Stores leak readings for tone-hole tests.
Recommendations: Add validation for reading value and test date.

[repair_portal/lab/doctype/leak_test/leak_test.py]
Purpose: Parent DocType for tone-hole leak tests.
Class: `LeakTest(Document)`
- Stores leak test data for instruments.
Recommendations: Add validation for test completeness and instrument linkage.

[repair_portal/lab/doctype/measurement_entry/measurement_entry.py]
Purpose: Server-side logic for Measurement Entry child table.
Class: `MeasurementEntry(Document)`
- Stores measurement entries for lab analysis.
Recommendations: Add validation for measurement type and value.

[repair_portal/lab/doctype/measurement_session/measurement_session.py]
Purpose: Server-side logic for Measurement Session doctype.
Class: `MeasurementSession(Document)`
- Validates instrument selection for measurement sessions.
Recommendations: Add validation for session completeness and measurement types.

[repair_portal/lab/doctype/reed_match_result/reed_match_result.py]
Purpose: Parent DocType storing reed match results.
Class: `ReedMatchResult(Document)`
- Stores reed match results for lab analysis.
Recommendations: Add validation for match accuracy and instrument linkage.

[repair_portal/lab/doctype/tone_analyzer/tone_analyzer.py]
Purpose: Server-side controller for Tone & Intonation Analyzer; handles batch audio processing, spectrogram generation, and data persistence.
Class: `ToneIntonationAnalyzer(Document)`
- Processes audio files, extracts acoustic features, and generates visual artifacts.
Recommendations: Add error handling for audio processing and improve feature extraction logic.

[repair_portal/lab/doctype/tone_fitness_entry/tone_fitness_entry.py]
Purpose: Child table for tone fitness trend entries.
Class: `ToneFitnessEntry(Document)`
- Stores tone fitness trend data for lab analysis.
Recommendations: Add validation for entry value and trend accuracy.

[repair_portal/lab/doctype/tone_fitness/tone_fitness.py]
Purpose: Parent DocType for brightness vs warmth measurements.
Class: `ToneFitness(Document)`
- Stores brightness and warmth measurements for instruments.
Recommendations: Add validation for measurement completeness and instrument linkage.

[repair_portal/lab/doctype/tone_intonation_analyzer/tone_intonation_analyzer.py]
Purpose: Enterprise-grade server-side controller for acoustic analysis; manages backend logic for tone and intonation analysis.
Class: `ToneIntonationAnalyzer(Document)`
- Processes audio, generates spectrograms, and manages baseline data.
Recommendations: Add error handling for DSP library availability and improve analysis logic.

[repair_portal/lab/page/impedance_recorder/impedance_recorder.py]
Purpose: Desk page for recording impedance data via mic; technician-only access.
Function: `get_context(context)`
- Checks technician role before allowing access.
Recommendations: Add error handling for permission checks and improve context rendering.

[repair_portal/lab/page/intonation_recorder/intonation_recorder.py]
Purpose: Technician-only desk page for recording clarinet intonation audio.
Function: `get_context(context)`
- Checks technician role before allowing access.
Recommendations: Add error handling for permission checks and improve context rendering.

[repair_portal/lab/page/leak_test_recorder/leak_test_recorder.py]
Purpose: Desk page for capturing leak decay via mic; technician-only access.
Function: `get_context(context)`
- Checks technician role before allowing access.
Recommendations: Add error handling for permission checks and improve context rendering.

[repair_portal/lab/page/recording_analyzer/recording_analyzer.py]
Purpose: Server stub for Recording Analyzer page; used for route-based permission checks and hooks.
Recommendations: Add implementation for recording analysis and improve permission logic.

[repair_portal/player_profile/doctype/player_equipment_preference/player_equipment_preference.py]
Purpose: Controller for Player Equipment Preference child table; captures all equipment choices for simplified player profiling.
Class: `PlayerEquipmentPreference(Document)`
- Stores preferences for mouthpiece, ligature, reed, barrel, and instrument.
Recommendations: Add validation for equipment type and completeness.

[repair_portal/player_profile/doctype/player_profile/player_profile.py]
Purpose: Core business logic and automation for Player Profile (CRM); covers musician lifecycle, preferences, marketing, compliance, and CRM triggers.
Class: `PlayerProfile(Document)`
- Handles identity, musical, equipment, service preferences, analytics, permissions, and CRM automations.
Recommendations: Add error handling for CRM triggers and improve compliance logic.

[repair_portal/qa/doctype/final_qa_checklist/final_qa_checklist.py]
Purpose: Validates QA checklist completion, updates Instrument Profile status, and logs errors on submit.
Class: `FinalQaChecklist(Document)`
- Validates checklist items and updates instrument profile status on submit.
Recommendations: Add error handling for status updates and improve checklist validation.

[repair_portal/qa/doctype/final_qa_checklist_item/final_qa_checklist_item.py]
Purpose: Controller for Final QA Checklist Item Doctype.
Class: `FinalQaChecklistItem(Document)`
- Stores QA checklist items for final review.
Recommendations: Add validation for item completeness and review status.

[repair_portal/repair/doctype/default_operations/default_operations.py]
Purpose: Handles default operations for repair processes, including inventory management and maintenance rules.
Class: `DefaultOperations(Document)`
- Validates operation type, manages inventory, maintenance, and repair logic.
Recommendations: Add error handling for blocked operations and improve business rule enforcement.

[repair_portal/repair/doctype/operation_template/operation_template.py]
Purpose: Controller for Operation Template DocType; manages setup/repair operation blueprints.
Class: `OperationTemplate(Document)`
- Stores blueprint for operations, components, and completion status.
Recommendations: Add validation for operation completeness and improve template logic.

[repair_portal/repair/doctype/pulse_update/pulse_update.py]
Purpose: Controller for Pulse Update entries linked to Repair Orders.
Class: `PulseUpdate(Document)`
- Stores pulse updates for repair orders.
Recommendations: Add validation for update type and timestamp.

[repair_portal/repair/doctype/repair_feedback/repair_feedback.py]
Purpose: Backend logic for storing customer repair feedback.
Class: `RepairFeedback(Document)`
- Validates repair order and rating; stores feedback for repairs.
Recommendations: Add validation for feedback text and improve rating logic.

[repair_portal/repair/doctype/repair_issue/repair_issue.py]
Purpose: Server-side logic for Repair Issue doctype.
Class: `RepairIssue(Document)`
- Validates customer, generates name, and handles submission logic.
Recommendations: Add error handling for missing customer and improve issue tracking.

[repair_portal/repair/doctype/repair_order/repair_order.py]
Purpose: Unified controller logic for Repair Order; merges Repair Request and adds robust error logging, docstrings, and automation hooks.
Class: `RepairOrder(Document)`
- Validates required fields, handles warranty logic, and manages submission automation.
Recommendations: Add error handling for warranty logic and improve automation hooks.

[repair_portal/repair_logging/doctype/barcode_scan_entry/barcode_scan_entry.py]
Purpose: Captures and resolves barcode usage for item lookup during repairs.
Class: `BarcodeScanEntry(Document)`
- Stores barcode scan entries for repair processes.
Recommendations: Add validation for barcode format and item linkage.

[repair_portal/repair_logging/doctype/diagnostic_metrics/diagnostic_metrics.py]
Purpose: Child table to record diagnostic measurements.
Class: `DiagnosticMetrics(Document)`
- Stores diagnostic metrics for repair analysis.
Recommendations: Add validation for measurement type and value.

[repair_portal/repair_logging/doctype/instrument_interaction_log/instrument_interaction_log.py]
Purpose: Logs individual interaction entries tied to an instrument for historical tracking.
Class: `InstrumentInteractionLog(Document)`
- Stores interaction logs for instrument history.
Recommendations: Add validation for interaction type and timestamp.

[repair_portal/repair_logging/doctype/key_measurement/key_measurement.py]
Purpose: Child table for individual key/pad measurements during inspection.
Class: `KeyMeasurement(Document)`
- Stores key and pad measurements for instrument inspection.
Recommendations: Add validation for measurement accuracy and completeness.

[repair_portal/repair_logging/doctype/material_use_log/material_use_log.py]
Purpose: Enforces validation and decrements stock when material is used.
Class: `MaterialUseLog(Document)`
- Validates quantity and item existence; creates stock entry on submit.
Recommendations: Add error handling for stock entry creation and improve inventory validation.

[repair_portal/repair_logging/doctype/pad_condition/pad_condition.py]
Purpose: Server-side logic for Pad Condition child table.
Class: `PadCondition(Document)`
- Stores pad condition data for instrument repairs.
Recommendations: Add validation for condition type and pad linkage.

[repair_portal/repair_logging/doctype/related_instrument_interaction/related_instrument_interaction.py]
Purpose: Tracks interactions related to instruments in linked Customer and Item documents.
Class: `RelatedInstrumentInteraction(Document)`
- Stores related interaction entries for audit and history.
Recommendations: Add validation for interaction type and related document linkage.

[repair_portal/repair_logging/doctype/repair_parts_used/repair_parts_used.py]
Purpose: Tracks parts used in repairs, including item details and quantities; maintains inventory accuracy.
Class: `RepairPartsUsed(Document)`
- Validates part usage, inventory availability, and creates stock entry on submit.
Recommendations: Add error handling for inventory updates and improve part usage validation.

[repair_portal/repair_logging/doctype/repair_task_log/repair_task_log.py]
Purpose: Ensures audit and change log for all repair log actions; SOX/ISO/FDA audit logging included.
Class: `RepairTaskLog(Document)`
- Sets logged_by to session user; logs unauthorized modification attempts.
Recommendations: Add validation for log completeness and improve audit logic.

[repair_portal/repair_logging/doctype/tenon_measurement/tenon_measurement.py]
Purpose: Manages tenon measurements for repair logging.
Class: `TenonMeasurement(Document)`
- Tracks measurements related to tenon repairs; provides hooks for lifecycle events.
Recommendations: Add validation for measurement accuracy and improve lifecycle event logic.

[repair_portal/repair_logging/doctype/tone_hole_inspection_record/tone_hole_inspection_record.py]
Purpose: Child table for documenting tone hole visual inspection results.
Class: `ToneHoleInspectionRecord(Document)`
- Validates tone hole number, visual status, and photo attachment.
Recommendations: Add error handling for missing documentation and improve inspection completeness.

[repair_portal/repair_logging/doctype/tool_usage_log/tool_usage_log.py]
Purpose: Tracks technician tool usage during repair tasks.
Class: `ToolUsageLog(Document)`
- Stores tool usage logs for repair tasks.
Recommendations: Add validation for tool type and usage notes.

[repair_portal/repair_logging/doctype/visual_inspection/visual_inspection.py]
Purpose: Validation and lifecycle hooks for Visual Inspection entries.
Class: `VisualInspection(Document)`
- Stores visual inspection data for repairs.
Recommendations: Add validation for inspection completeness and image attachment.

[repair_portal/repair_logging/doctype/warranty_modification_log/warranty_modification_log.py]
Purpose: Backend controller for warranty change logs.
Class: `WarrantyModificationLog(Document)`
- Stores warranty modification logs for instruments.
Recommendations: Add validation for modification type and date.

[repair_portal/repair_logging/report/repair_tasks_by_type/repair_tasks_by_type.py]
Purpose: Report for repair tasks by type, with date range and technician filters, and chart data.
Function: `execute(filters=None)`
- Aggregates repair tasks by type and returns chart data.
Recommendations: Add more granular filtering and improve chart visualization.

[repair_portal/repair_portal/doctype/pulse_update/pulse_update.py]
Purpose: Single progress update against a Repair Request; includes whitelisted endpoint for real-time updates.
Class: `PulseUpdate(Document)`
- Validates update time and percent complete; provides API for creating updates.
Recommendations: Add error handling for real-time events and improve update validation.

[repair_portal/repair_portal/doctype/qa_checklist_item/qa_checklist_item.py]
Purpose: Controller for QA Checklist Item child table.
Class: `QaChecklistItem(Document)`
- Stores QA checklist items for repair QA.
Recommendations: Add validation for item completeness and review status.

[repair_portal/repair_portal/doctype/technician/technician.py]
Purpose: Technician master data, onboarding, and activity audit logic.
Class: `Technician(Document)`
- Validates email and phone, sends onboarding email, and tracks activity.
Recommendations: Add error handling for onboarding and improve audit logic.
