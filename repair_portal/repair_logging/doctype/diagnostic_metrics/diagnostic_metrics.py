# Path: repair_portal/repair_logging/doctype/diagnostic_metrics/diagnostic_metrics.py
# Date: 2025-01-14
# Version: 2.0.0
# Description: Production-ready diagnostic metrics collection with validation, performance analysis, and audit compliance
# Dependencies: frappe, frappe.model.document, frappe.utils

import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


class DiagnosticMetrics(Document):
    """
    Diagnostic Metrics: Collect and validate diagnostic measurements for repair analysis.
    """

    def validate(self):
        """Validate diagnostic metrics with comprehensive business rules."""
        self._validate_required_fields()
        self._validate_measurement_data()
        self._validate_metric_ranges()
        self._validate_instrument_reference()
        self._validate_technician_qualifications()

    def before_insert(self):
        """Set defaults and process measurements."""
        self._set_measurement_timestamp()
        self._normalize_metric_data()
        self._calculate_diagnostic_score()
        self._log_diagnostic_audit()

    def before_save(self):
        """Update calculations and validations before saving."""
        self._update_metric_calculations()
        self._validate_data_integrity()

    def on_submit(self):
        """Process diagnostic completion with proper validation."""
        self._validate_diagnostic_completion()
        self._generate_diagnostic_report()
        self._update_instrument_status()

    def _validate_required_fields(self):
        """Validate all required fields are present."""
        required_fields = ["measurement_type", "measured_value"]
        missing = [field for field in required_fields if not self.get(field)]
        if missing:
            frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))

    def _validate_measurement_data(self):
        """Validate measurement data format and consistency."""
        if self.measured_value is None:
            frappe.throw(_("Measured value is required"))

        # Validate numeric measurements
        if self.measurement_type in ["Temperature", "Pressure", "Frequency", "Voltage"]:
            try:
                float(self.measured_value)
            except (ValueError, TypeError):
                frappe.throw(_("Measured value must be numeric for {0}").format(self.measurement_type))

        # Validate JSON data fields
        if self.raw_data:
            try:
                json.loads(self.raw_data)
            except json.JSONDecodeError:
                frappe.throw(_("Raw data must be valid JSON format"))

    def _validate_metric_ranges(self):
        """Validate measurements are within acceptable ranges."""
        measurement_ranges = {
            "Temperature": {"min": -50, "max": 200, "unit": "°C"},
            "Pressure": {"min": 0, "max": 1000, "unit": "PSI"},
            "Frequency": {"min": 0, "max": 20000, "unit": "Hz"},
            "Voltage": {"min": -50, "max": 50, "unit": "V"},
            "Resistance": {"min": 0, "max": 1000000, "unit": "Ω"},
        }

        if self.measurement_type in measurement_ranges:
            range_info = measurement_ranges[self.measurement_type]
            value = flt(self.measured_value)

            if value < range_info["min"] or value > range_info["max"]:
                frappe.msgprint(
                    _("Warning: {0} value ({1}) is outside normal range ({2} to {3} {4})").format(
                        self.measurement_type, value, range_info["min"], range_info["max"], range_info["unit"]
                    ),
                    alert=True,
                )

    def _validate_instrument_reference(self):
        """Validate instrument reference and access permissions."""
        if self.instrument_reference:
            if not frappe.db.exists("Instrument Profile", self.instrument_reference):
                frappe.throw(_("Instrument reference {0} does not exist").format(self.instrument_reference))

            # Check read permission on instrument
            if not frappe.has_permission("Instrument Profile", "read", self.instrument_reference):
                frappe.throw(_("No permission to access instrument {0}").format(self.instrument_reference))

    def _validate_technician_qualifications(self):
        """Validate technician is qualified for diagnostic measurements."""
        if self.measured_by:
            # Verify technician exists and is active
            technician_data = frappe.db.get_value("User", self.measured_by, ["enabled", "full_name"])

            if not technician_data or not technician_data[0]:
                frappe.throw(_("Technician {0} is not active in the system.").format(self.measured_by))

            # Check if user has diagnostic certification
            if not frappe.db.exists(
                "Has Role",
                {"parent": self.measured_by, "role": ["in", ["Technician", "Diagnostic Specialist"]]},
            ):
                frappe.msgprint(
                    _("Warning: User {0} may not be certified for diagnostic measurements.").format(
                        self.measured_by
                    )
                )

    def _set_measurement_timestamp(self):
        """Set measurement timestamp if not specified."""
        if not self.measurement_timestamp:
            self.measurement_timestamp = now_datetime()

    def _normalize_metric_data(self):
        """Normalize and standardize metric data format."""
        if self.measurement_unit and self.measured_value:
            # Convert common unit variations to standard units
            unit_conversions = {
                "celsius": "°C",
                "fahrenheit": "°F",
                "hertz": "Hz",
                "volts": "V",
                "amps": "A",
                "ohms": "Ω",
            }

            normalized_unit = unit_conversions.get(self.measurement_unit.lower(), self.measurement_unit)
            self.measurement_unit = normalized_unit

    def _calculate_diagnostic_score(self):
        """Calculate diagnostic score based on measurement quality."""
        if self.measurement_type and self.measured_value:
            # Basic scoring algorithm - can be enhanced based on requirements
            score = 100  # Start with perfect score

            # Reduce score for out-of-range values
            if self.is_out_of_range():
                score -= 30

            # Reduce score for incomplete measurements
            if not self.measurement_unit:
                score -= 10

            if not self.calibration_reference:
                score -= 5

            self.diagnostic_score = max(0, score)

    def _update_metric_calculations(self):
        """Update derived calculations and metrics."""
        # Recalculate diagnostic score
        self._calculate_diagnostic_score()

        # Update analysis flags
        self.requires_attention = self.is_out_of_range() or (
            self.diagnostic_score and self.diagnostic_score < 70
        )

    def _validate_data_integrity(self):
        """Validate data integrity and consistency."""
        # Check for duplicate measurements
        if self.measurement_type and self.instrument_reference and self.measurement_timestamp:
            existing = frappe.db.exists(
                self.doctype,
                {
                    "name": ["!=", self.name],
                    "measurement_type": self.measurement_type,
                    "instrument_reference": self.instrument_reference,
                    "measurement_timestamp": self.measurement_timestamp,
                },
            )

            if existing:
                frappe.msgprint(_("Warning: Similar measurement already exists: {0}").format(existing))

    def _validate_diagnostic_completion(self):
        """Validate diagnostic is complete before submission."""
        if not self.measured_by:
            frappe.throw(_("Measured by field is required for submission"))

        if not self.measurement_timestamp:
            frappe.throw(_("Measurement timestamp is required for submission"))

        if self.requires_attention and not self.technician_notes:
            frappe.throw(_("Technician notes are required for measurements requiring attention"))

    def _generate_diagnostic_report(self):
        """Generate comprehensive diagnostic report."""
        report_data = {
            "measurement_type": self.measurement_type,
            "measured_value": self.measured_value,
            "measurement_unit": self.measurement_unit,
            "diagnostic_score": self.diagnostic_score,
            "requires_attention": self.requires_attention,
            "measured_by": self.measured_by,
            "measurement_timestamp": self.measurement_timestamp,
            "instrument_reference": self.instrument_reference,
        }

        # Store report data
        self.diagnostic_report = json.dumps(report_data, indent=2, default=str)

    def _update_instrument_status(self):
        """Update instrument status based on diagnostic results."""
        if self.instrument_reference and self.requires_attention:
            try:
                instrument = frappe.get_doc("Instrument Profile", self.instrument_reference)

                # Add diagnostic flag or update status if needed
                if hasattr(instrument, "diagnostic_alerts"):
                    alerts = json.loads(instrument.diagnostic_alerts or "[]")
                    alerts.append(
                        {
                            "type": self.measurement_type,
                            "timestamp": str(self.measurement_timestamp),
                            "score": self.diagnostic_score,
                        }
                    )
                    instrument.db_set("diagnostic_alerts", json.dumps(alerts))

                frappe.logger("diagnostic_tracking").info(
                    {
                        "action": "instrument_status_updated",
                        "instrument": self.instrument_reference,
                        "diagnostic_score": self.diagnostic_score,
                        "requires_attention": self.requires_attention,
                    }
                )

            except Exception as e:
                frappe.log_error(f"Failed to update instrument status: {str(e)}")

    def _log_diagnostic_audit(self):
        """Log diagnostic measurement for audit compliance."""
        frappe.logger("diagnostic_audit").info(
            {
                "action": "diagnostic_measurement",
                "measurement_type": self.measurement_type,
                "measured_value": self.measured_value,
                "measured_by": self.measured_by,
                "instrument_reference": self.instrument_reference,
                "user": frappe.session.user,
                "timestamp": frappe.utils.now(),
            }
        )

    def is_out_of_range(self):
        """Check if measurement is outside acceptable range."""
        measurement_ranges = {
            "Temperature": {"min": -50, "max": 200},
            "Pressure": {"min": 0, "max": 1000},
            "Frequency": {"min": 0, "max": 20000},
            "Voltage": {"min": -50, "max": 50},
            "Resistance": {"min": 0, "max": 1000000},
        }

        if self.measurement_type in measurement_ranges:
            range_info = measurement_ranges[self.measurement_type]
            value = flt(self.measured_value)
            return value < range_info["min"] or value > range_info["max"]

        return False

    @frappe.whitelist()
    def recalculate_metrics(self):
        """Recalculate diagnostic metrics and scores."""
        if not frappe.has_permission(self.doctype, "write", self.name):
            frappe.throw(_("No permission to recalculate metrics"))

        self._calculate_diagnostic_score()
        self._update_metric_calculations()
        self.save()

        frappe.logger("diagnostic_tracking").info(
            {
                "action": "metrics_recalculated",
                "document": self.name,
                "new_score": self.diagnostic_score,
                "user": frappe.session.user,
            }
        )

        return {"message": "Metrics recalculated successfully", "score": self.diagnostic_score}
