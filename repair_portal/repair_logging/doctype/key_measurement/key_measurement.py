# Path: repair_portal/repair_logging/doctype/key_measurement/key_measurement.py
# Date: 2025-01-14
# Version: 2.0.0
# Description: Production-ready key measurement tracking with validation, calibration compliance, and audit logging
# Dependencies: frappe, frappe.model.document, frappe.utils

import json
import statistics

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, now_datetime


class KeyMeasurement(Document):
    """
    Key Measurement: Track critical measurements with validation and calibration compliance.
    """

    def validate(self):
        """Validate key measurement with comprehensive business rules."""
        self._validate_required_fields()
        self._validate_measurement_data()
        self._validate_measurement_ranges()
        self._validate_instrument_calibration()
        self._validate_technician_certification()

    def before_insert(self):
        """Set defaults and process measurement data."""
        self._set_measurement_timestamp()
        self._normalize_measurement_units()
        self._calculate_measurement_statistics()
        self._log_measurement_audit()

    def before_save(self):
        """Update calculations and validations before saving."""
        self._update_quality_indicators()
        self._validate_measurement_accuracy()

    def on_submit(self):
        """Process measurement completion with proper validation."""
        self._validate_measurement_completion()
        self._update_instrument_measurement_history()
        self._check_tolerance_compliance()

    def _validate_required_fields(self):
        """Validate all required fields are present."""
        required_fields = ["measurement_name", "measured_value"]
        missing = [field for field in required_fields if not self.get(field)]
        if missing:
            frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))

    def _validate_measurement_data(self):
        """Validate measurement data format and consistency."""
        if self.measured_value is None:
            frappe.throw(_("Measured value is required"))

        # Validate numeric measurements
        try:
            float(self.measured_value)
        except (ValueError, TypeError):
            frappe.throw(_("Measured value must be numeric"))

        # Validate measurement range
        if flt(self.measured_value) < 0 and self.measurement_name not in ["Temperature", "Voltage"]:
            frappe.msgprint(_("Warning: Negative measurement value detected"))

        # Validate JSON data fields
        if self.raw_measurement_data:
            try:
                json.loads(self.raw_measurement_data)
            except json.JSONDecodeError:
                frappe.throw(_("Raw measurement data must be valid JSON format"))

    def _validate_measurement_ranges(self):
        """Validate measurements are within expected ranges."""
        measurement_ranges = {
            "Length": {"min": 0, "max": 1000, "unit": "mm"},
            "Weight": {"min": 0, "max": 50, "unit": "kg"},
            "Temperature": {"min": -40, "max": 150, "unit": "°C"},
            "Pressure": {"min": 0, "max": 500, "unit": "kPa"},
            "Frequency": {"min": 0, "max": 20000, "unit": "Hz"},
            "Voltage": {"min": -100, "max": 100, "unit": "V"},
            "Current": {"min": 0, "max": 50, "unit": "A"},
            "Resistance": {"min": 0, "max": 100000, "unit": "Ω"},
        }

        if self.measurement_name in measurement_ranges:
            range_info = measurement_ranges[self.measurement_name]
            value = flt(self.measured_value)

            if value < range_info["min"] or value > range_info["max"]:
                frappe.msgprint(
                    _("Warning: {0} value ({1}) is outside normal range ({2} to {3} {4})").format(
                        self.measurement_name, value, range_info["min"], range_info["max"], range_info["unit"]
                    ),
                    alert=True,
                )
                self.out_of_range = 1

    def _validate_instrument_calibration(self):
        """Validate measurement instrument calibration status."""
        if self.measuring_instrument:
            if not frappe.db.exists("Tool", self.measuring_instrument):
                frappe.throw(_("Measuring instrument {0} does not exist").format(self.measuring_instrument))

            # Check calibration status
            tool_data = frappe.db.get_value(
                "Tool",
                self.measuring_instrument,
                ["last_calibration_date", "calibration_due_date", "calibration_status"],
            )

            if tool_data:
                last_cal, due_date, status = tool_data

                if status != "Calibrated":
                    frappe.throw(
                        _("Measuring instrument {0} is not properly calibrated").format(
                            self.measuring_instrument
                        )
                    )

                if due_date and getdate(due_date) < getdate():
                    frappe.throw(
                        _("Measuring instrument {0} calibration is overdue").format(self.measuring_instrument)
                    )

    def _validate_technician_certification(self):
        """Validate technician is certified for precision measurements."""
        if self.measured_by:
            # Verify technician exists and is active
            technician_data = frappe.db.get_value("User", self.measured_by, ["enabled", "full_name"])

            if not technician_data or not technician_data[0]:
                frappe.throw(_("Technician {0} is not active in the system.").format(self.measured_by))

            # Check for measurement certification
            required_roles = ["Technician", "Quality Inspector", "Measurement Specialist"]
            user_roles = frappe.get_roles(self.measured_by)

            if not any(role in user_roles for role in required_roles):
                frappe.msgprint(
                    _("Warning: User {0} may not be certified for precision measurements.").format(
                        self.measured_by
                    )
                )

    def _set_measurement_timestamp(self):
        """Set measurement timestamp if not specified."""
        if not self.measurement_timestamp:
            self.measurement_timestamp = now_datetime()

    def _normalize_measurement_units(self):
        """Normalize and standardize measurement units."""
        if self.measurement_unit:
            # Convert common unit variations to standard units
            unit_conversions = {
                "millimeter": "mm",
                "millimeters": "mm",
                "centimeter": "cm",
                "centimeters": "cm",
                "meter": "m",
                "meters": "m",
                "kilogram": "kg",
                "kilograms": "kg",
                "gram": "g",
                "grams": "g",
                "celsius": "°C",
                "fahrenheit": "°F",
                "hertz": "Hz",
                "volts": "V",
                "amperes": "A",
                "amps": "A",
                "ohms": "Ω",
            }

            normalized_unit = unit_conversions.get(self.measurement_unit.lower(), self.measurement_unit)
            self.measurement_unit = normalized_unit

    def _calculate_measurement_statistics(self):
        """Calculate measurement statistics and quality indicators."""
        if self.repeat_measurements:
            try:
                # Parse repeat measurements from JSON
                repeat_data = json.loads(self.repeat_measurements)
                values = [float(val) for val in repeat_data if val is not None]

                if len(values) >= 2:
                    # Calculate statistical measures
                    self.measurement_mean = statistics.mean(values)
                    self.measurement_std_dev = statistics.stdev(values) if len(values) > 1 else 0
                    self.measurement_range = max(values) - min(values)

                    # Calculate coefficient of variation (precision indicator)
                    if self.measurement_mean != 0:
                        self.coefficient_of_variation = (
                            self.measurement_std_dev / self.measurement_mean
                        ) * 100

                    # Quality flag based on precision
                    if self.coefficient_of_variation and self.coefficient_of_variation > 5:
                        self.precision_warning = 1

            except (json.JSONDecodeError, ValueError, TypeError):
                frappe.msgprint(_("Warning: Invalid repeat measurements data format"))

    def _update_quality_indicators(self):
        """Update quality indicators and flags."""
        # Reset quality flags
        self.out_of_range = 0
        self.precision_warning = 0

        # Recalculate range validation
        self._validate_measurement_ranges()

        # Recalculate statistics if needed
        if self.repeat_measurements:
            self._calculate_measurement_statistics()

    def _validate_measurement_accuracy(self):
        """Validate measurement accuracy against standards."""
        # Check if measurement has target value
        if self.target_value and self.measured_value:
            deviation = abs(flt(self.measured_value) - flt(self.target_value))

            if self.tolerance_value:
                if deviation > flt(self.tolerance_value):
                    self.out_of_tolerance = 1
                    frappe.msgprint(
                        _("Warning: Measurement deviation ({0}) exceeds tolerance ({1})").format(
                            deviation, self.tolerance_value
                        ),
                        alert=True,
                    )
                else:
                    self.out_of_tolerance = 0

            # Calculate accuracy percentage
            if self.target_value != 0:
                accuracy = (1 - (deviation / abs(flt(self.target_value)))) * 100
                self.accuracy_percentage = max(0, accuracy)

    def _validate_measurement_completion(self):
        """Validate measurement is complete before submission."""
        if not self.measured_by:
            frappe.throw(_("Measured by field is required for submission"))

        if not self.measurement_timestamp:
            frappe.throw(_("Measurement timestamp is required for submission"))

        if self.out_of_tolerance and not self.corrective_action:
            frappe.throw(_("Corrective action is required for out-of-tolerance measurements"))

    def _update_instrument_measurement_history(self):
        """Update instrument's measurement history."""
        if self.instrument_reference:
            try:
                # Store measurement in instrument history
                measurement_record = {
                    "measurement_name": self.measurement_name,
                    "measured_value": self.measured_value,
                    "measurement_unit": self.measurement_unit,
                    "timestamp": str(self.measurement_timestamp),
                    "measured_by": self.measured_by,
                    "out_of_tolerance": self.out_of_tolerance,
                    "accuracy_percentage": self.accuracy_percentage,
                }

                # Update instrument with latest measurement data
                instrument = frappe.get_doc("Instrument Profile", self.instrument_reference)

                if hasattr(instrument, "measurement_history"):
                    history = json.loads(instrument.measurement_history or "[]")
                    history.append(measurement_record)
                    # Keep only last 100 measurements
                    history = history[-100:]
                    instrument.db_set("measurement_history", json.dumps(history))

                frappe.logger("measurement_tracking").info(
                    {
                        "action": "instrument_measurement_updated",
                        "instrument": self.instrument_reference,
                        "measurement": self.measurement_name,
                        "value": self.measured_value,
                        "out_of_tolerance": self.out_of_tolerance,
                    }
                )

            except Exception as e:
                frappe.log_error(f"Failed to update instrument measurement history: {str(e)}")

    def _check_tolerance_compliance(self):
        """Check tolerance compliance and create alerts if needed."""
        if self.out_of_tolerance:
            # Create compliance alert
            try:
                alert = frappe.get_doc(
                    {
                        "doctype": "ToDo",
                        "description": f"Out-of-tolerance measurement: {self.measurement_name} on {self.instrument_reference}",
                        "reference_type": self.doctype,
                        "reference_name": self.name,
                        "assigned_by": frappe.session.user,
                        "priority": "High",
                    }
                )
                alert.insert()

                frappe.logger("compliance_tracking").warning(
                    {
                        "action": "tolerance_violation",
                        "measurement": self.name,
                        "deviation": abs(flt(self.measured_value) - flt(self.target_value or 0)),
                        "tolerance": self.tolerance_value,
                        "alert_created": alert.name,
                    }
                )

            except Exception as e:
                frappe.log_error(f"Failed to create tolerance compliance alert: {str(e)}")

    def _log_measurement_audit(self):
        """Log measurement for audit compliance."""
        frappe.logger("measurement_audit").info(
            {
                "action": "key_measurement_recorded",
                "measurement_name": self.measurement_name,
                "measured_value": self.measured_value,
                "measurement_unit": self.measurement_unit,
                "measured_by": self.measured_by,
                "measuring_instrument": self.measuring_instrument,
                "instrument_reference": self.instrument_reference,
                "user": frappe.session.user,
                "timestamp": str(self.measurement_timestamp),
            }
        )

    @frappe.whitelist()
    def recalculate_statistics(self):
        """Recalculate measurement statistics and quality indicators."""
        if not frappe.has_permission(self.doctype, "write", self.name):
            frappe.throw(_("No permission to recalculate statistics"))

        self._calculate_measurement_statistics()
        self._update_quality_indicators()
        self._validate_measurement_accuracy()
        self.save()

        frappe.logger("measurement_tracking").info(
            {"action": "statistics_recalculated", "measurement": self.name, "user": frappe.session.user}
        )

        return {
            "message": "Statistics recalculated successfully",
            "accuracy_percentage": self.accuracy_percentage,
            "out_of_tolerance": self.out_of_tolerance,
        }

    @frappe.whitelist()
    def add_repeat_measurement(self, value):
        """Add a repeat measurement value."""
        if not frappe.has_permission(self.doctype, "write", self.name):
            frappe.throw(_("No permission to add repeat measurements"))

        try:
            float(value)
        except (ValueError, TypeError):
            frappe.throw(_("Repeat measurement value must be numeric"))

        # Add to repeat measurements
        current_data = json.loads(self.repeat_measurements or "[]")
        current_data.append(float(value))

        self.db_set("repeat_measurements", json.dumps(current_data))

        # Recalculate statistics
        self._calculate_measurement_statistics()
        self.save()

        frappe.logger("measurement_tracking").info(
            {
                "action": "repeat_measurement_added",
                "measurement": self.name,
                "value": value,
                "user": frappe.session.user,
            }
        )

        return {"message": "Repeat measurement added successfully"}
