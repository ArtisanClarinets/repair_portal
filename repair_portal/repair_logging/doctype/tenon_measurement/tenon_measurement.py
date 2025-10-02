# Path: repair_portal/repair_logging/doctype/tenon_measurement/tenon_measurement.py
# Date: 2025-01-14
# Version: 2.0.0
# Description: Production-ready tenon measurement tracking with precision validation and audit compliance
# Dependencies: frappe, frappe.model.document, frappe.utils

import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, now_datetime


class TenonMeasurement(Document):
    """
    Tenon Measurement: Track precise tenon dimensions and fit measurements for instrument repair.
    Critical for maintaining proper joint fit and assembly tolerances.
    """

    def validate(self):
        """Validate tenon measurement data with precision and compliance requirements."""
        self._validate_required_fields()
        self._validate_measurement_values()
        self._validate_instrument_reference()
        self._validate_technician_permissions()
        self._validate_measurement_tools()

    def before_insert(self):
        """Set defaults and validate measurement setup."""
        self._set_measurement_timestamp()
        self._normalize_measurement_data()
        self._validate_measurement_conditions()
        self._log_measurement_audit()

    def before_save(self):
        """Update calculations and validations before saving."""
        self._calculate_tolerance_analysis()
        self._update_measurement_metadata()
        self._validate_measurement_consistency()

    def on_submit(self):
        """Process measurement completion with proper validation."""
        self._validate_measurement_completion()
        self._update_instrument_history()
        self._check_fit_requirements()
        self._generate_measurement_report()

    def _validate_required_fields(self):
        """Validate all required measurement fields are present."""
        required_fields = ["instrument_profile", "tenon_location", "measurement_type"]
        missing = [field for field in required_fields if not self.get(field)]
        if missing:
            frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))

    def _validate_measurement_values(self):
        """Validate measurement values for precision and reasonableness."""
        # Validate diameter measurements
        if self.diameter_measurement:
            diameter = flt(self.diameter_measurement)
            if diameter <= 0:
                frappe.throw(_("Diameter measurement must be positive"))
            if diameter > 30:  # 30mm is extremely large for clarinet tenons
                frappe.throw(_("Diameter measurement {0}mm seems unreasonably large").format(diameter))
            if diameter < 8:  # 8mm is very small for most tenons
                frappe.msgprint(_("Warning: Diameter measurement {0}mm is unusually small").format(diameter))
        
        # Validate length measurements
        if self.length_measurement:
            length = flt(self.length_measurement)
            if length <= 0:
                frappe.throw(_("Length measurement must be positive"))
            if length > 100:  # 100mm is extremely long for tenons
                frappe.throw(_("Length measurement {0}mm seems unreasonably large").format(length))
        
        # Validate taper measurements
        if self.taper_measurement:
            taper = flt(self.taper_measurement)
            if abs(taper) > 2:  # 2mm taper is very large
                frappe.msgprint(_("Warning: Taper measurement {0}mm is unusually large").format(taper))
        
        # Validate tolerance measurements
        if self.tolerance_measurement:
            tolerance = flt(self.tolerance_measurement)
            if abs(tolerance) > 0.5:  # 0.5mm tolerance is very large
                frappe.msgprint(_("Warning: Tolerance {0}mm exceeds typical precision requirements").format(tolerance))

    def _validate_instrument_reference(self):
        """Validate instrument reference exists and is accessible."""
        if self.instrument_profile:
            if not frappe.db.exists('Instrument Profile', self.instrument_profile):
                frappe.throw(_("Instrument Profile {0} does not exist").format(self.instrument_profile))
            
            if not frappe.has_permission("Instrument Profile", "read", self.instrument_profile):
                frappe.throw(_("No permission to access instrument {0}").format(self.instrument_profile))
            
            # Get instrument details for validation context
            instrument_data = frappe.db.get_value('Instrument Profile', self.instrument_profile, 
                ['instrument_type', 'instrument_model'], as_dict=True)
            
            if instrument_data and instrument_data.instrument_type:
                self.instrument_type = instrument_data.instrument_type

    def _validate_technician_permissions(self):
        """Validate technician has appropriate permissions for precision measurements."""
        if self.measured_by:
            # Verify technician exists and is active
            tech_data = frappe.db.get_value('User', self.measured_by, ['enabled', 'full_name'])
            
            if not tech_data or not tech_data[0]:
                frappe.throw(_('Technician {0} is not active in the system.').format(self.measured_by))
            
            # Check for appropriate measurement roles
            required_roles = ['Technician', 'Measurement Specialist', 'Quality Inspector', 'System Manager']
            user_roles = frappe.get_roles(self.measured_by)
            
            if not any(role in user_roles for role in required_roles):
                frappe.throw(_('User {0} does not have appropriate permissions for precision measurements.').format(self.measured_by))

    def _validate_measurement_tools(self):
        """Validate measurement tools and calibration."""
        valid_tools = [
            'Digital Calipers',
            'Micrometer',
            'Tenon Gauge',
            'Go/No-Go Gauge',
            'Precision Ruler',
            'Depth Gauge',
            'Pin Gauge Set',
            'Custom Jig'
        ]
        
        if self.measurement_tool and self.measurement_tool not in valid_tools:
            frappe.throw(_("Invalid measurement tool: {0}. Valid options are: {1}").format(
                self.measurement_tool, ', '.join(valid_tools)))
        
        # Validate calibration if tool specified
        if self.measurement_tool and self.tool_calibration_date:
            cal_date = getdate(self.tool_calibration_date)
            if cal_date > getdate():
                frappe.throw(_("Tool calibration date cannot be in the future"))

    def _set_measurement_timestamp(self):
        """Set measurement timestamp if not specified."""
        if not self.measurement_timestamp:
            self.measurement_timestamp = now_datetime()

    def _normalize_measurement_data(self):
        """Normalize and structure measurement data."""
        # Create structured measurement summary
        measurement_summary = {
            'instrument_profile': self.instrument_profile,
            'tenon_location': self.tenon_location,
            'measurement_type': self.measurement_type,
            'diameter': self.diameter_measurement,
            'length': self.length_measurement,
            'taper': self.taper_measurement,
            'tolerance': self.tolerance_measurement,
            'tool': self.measurement_tool,
            'technician': self.measured_by,
            'timestamp': str(self.measurement_timestamp)
        }
        
        # Store measurement metadata
        if not self.measurement_metadata:
            self.measurement_metadata = json.dumps(measurement_summary, indent=2, default=str)

    def _validate_measurement_conditions(self):
        """Validate measurement conditions and environment."""
        # Validate tenon location
        valid_locations = [
            'Upper Joint Tenon',
            'Lower Joint Tenon',
            'Barrel Tenon',
            'Bell Tenon',
            'Mouthpiece Receiver',
            'Custom Location'
        ]
        
        if self.tenon_location and self.tenon_location not in valid_locations:
            frappe.throw(_("Invalid tenon location: {0}").format(self.tenon_location))
        
        # Validate measurement type
        valid_types = [
            'Initial Measurement',
            'Work-in-Progress',
            'Final Measurement',
            'Quality Check',
            'Fit Test',
            'Tolerance Check'
        ]
        
        if self.measurement_type and self.measurement_type not in valid_types:
            frappe.throw(_("Invalid measurement type: {0}").format(self.measurement_type))
        
        # Validate environmental conditions if specified
        if self.temperature and (flt(self.temperature) < 10 or flt(self.temperature) > 40):
            frappe.msgprint(_("Warning: Temperature {0}°C is outside typical workshop range (10-40°C)").format(self.temperature))

    def _calculate_tolerance_analysis(self):
        """Calculate tolerance analysis and fit assessments."""
        if not (self.diameter_measurement and self.target_diameter):
            return
        
        measured_diameter = flt(self.diameter_measurement)
        target_diameter = flt(self.target_diameter)
        
        # Calculate deviation
        deviation = measured_diameter - target_diameter
        self.diameter_deviation = deviation
        
        # Determine fit status based on tolerance
        tolerance_limit = flt(self.tolerance_limit or 0.05)  # Default 0.05mm tolerance
        
        if abs(deviation) <= tolerance_limit:
            self.fit_status = 'Within Tolerance'
        elif deviation > tolerance_limit:
            self.fit_status = 'Oversized'
        else:
            self.fit_status = 'Undersized'
        
        # Calculate fit percentage
        if tolerance_limit > 0:
            fit_percentage = max(0, 100 - (abs(deviation) / tolerance_limit * 100))
            self.fit_percentage = fit_percentage

    def _update_measurement_metadata(self):
        """Update measurement metadata with current values."""
        try:
            metadata = json.loads(self.measurement_metadata or '{}')
            metadata.update({
                'last_modified': str(now_datetime()),
                'modified_by': frappe.session.user,
                'fit_status': self.fit_status,
                'deviation': self.diameter_deviation,
                'fit_percentage': self.fit_percentage
            })
            self.measurement_metadata = json.dumps(metadata, indent=2, default=str)
        except json.JSONDecodeError:
            # Reset metadata if corrupted
            self._normalize_measurement_data()

    def _validate_measurement_consistency(self):
        """Validate measurement data consistency."""
        # Check for reasonable relationships between measurements
        if self.diameter_measurement and self.length_measurement:
            diameter = flt(self.diameter_measurement)
            length = flt(self.length_measurement)
            
            # Sanity check: length should be reasonable relative to diameter
            if length < diameter / 2:
                frappe.msgprint(_("Warning: Length {0}mm is unusually short for diameter {1}mm").format(length, diameter))

    def _validate_measurement_completion(self):
        """Validate measurement is complete before submission."""
        if not self.measured_by:
            frappe.throw(_("Measured by field is required for submission"))
        
        if not self.measurement_timestamp:
            frappe.throw(_("Measurement timestamp is required for submission"))
        
        if not self.diameter_measurement:
            frappe.throw(_("Primary diameter measurement is required for submission"))
        
        if self.fit_status in ['Oversized', 'Undersized'] and not self.notes:
            frappe.throw(_("Notes are required when measurements are out of tolerance"))

    def _update_instrument_history(self):
        """Update instrument history with measurement data."""
        if not self.instrument_profile:
            return
            
        try:
            # Create measurement history entry
            measurement_record = {
                'measurement_id': self.name,
                'tenon_location': self.tenon_location,
                'measurement_type': self.measurement_type,
                'diameter': self.diameter_measurement,
                'length': self.length_measurement,
                'fit_status': self.fit_status,
                'deviation': self.diameter_deviation,
                'technician': self.measured_by,
                'timestamp': str(self.measurement_timestamp)
            }
            
            frappe.logger("tenon_measurement_history").info({
                "action": "measurement_recorded",
                "instrument_profile": self.instrument_profile,
                "measurement_data": measurement_record
            })
            
        except Exception as e:
            frappe.log_error(f"Failed to update instrument history: {str(e)}")

    def _check_fit_requirements(self):
        """Check fit requirements and generate alerts if needed."""
        if self.fit_status in ['Oversized', 'Undersized']:
            # Create alert for out-of-tolerance measurements
            alert_message = _("Tenon measurement out of tolerance: {0} at {1} ({2}mm deviation)").format(
                self.fit_status, self.tenon_location, abs(flt(self.diameter_deviation or 0)))
            
            frappe.msgprint(alert_message, alert=True)
            
            # Log quality alert
            frappe.logger("quality_alerts").warning({
                "action": "measurement_tolerance_exceeded",
                "instrument_profile": self.instrument_profile,
                "tenon_location": self.tenon_location,
                "fit_status": self.fit_status,
                "deviation": self.diameter_deviation,
                "technician": self.measured_by
            })

    def _generate_measurement_report(self):
        """Generate measurement report and recommendations."""
        if self.fit_status and self.fit_status != 'Within Tolerance':
            recommendations = []
            
            if self.fit_status == 'Oversized':
                recommendations.extend([
                    "Consider sanding or turning to reduce diameter",
                    "Check measurement tool calibration",
                    "Verify target specifications"
                ])
            elif self.fit_status == 'Undersized':
                recommendations.extend([
                    "Consider cork or tape wrapping to increase diameter",
                    "Evaluate tenon replacement options",
                    "Check for wear or damage"
                ])
            
            if recommendations and not self.recommendations:
                self.recommendations = '\n'.join(recommendations)

    def _log_measurement_audit(self):
        """Log tenon measurement for audit compliance."""
        frappe.logger("tenon_measurement_audit").info({
            "action": "tenon_measurement",
            "instrument_profile": self.instrument_profile,
            "tenon_location": self.tenon_location,
            "measurement_type": self.measurement_type,
            "diameter": self.diameter_measurement,
            "length": self.length_measurement,
            "fit_status": self.fit_status,
            "measured_by": self.measured_by,
            "tool": self.measurement_tool,
            "user": frappe.session.user,
            "timestamp": str(self.measurement_timestamp)
        })

    @frappe.whitelist()
    def get_measurement_history(self):
        """Get measurement history for this instrument and location."""
        if not frappe.has_permission(self.doctype, "read"):
            frappe.throw(_("No permission to view measurement history"))
        
        if not (self.instrument_profile and self.tenon_location):
            return []
        
        history = frappe.get_all(self.doctype,
            filters={
                'instrument_profile': self.instrument_profile,
                'tenon_location': self.tenon_location,
                'docstatus': ['!=', 2]
            },
            fields=[
                'name', 'measurement_timestamp', 'measurement_type', 
                'diameter_measurement', 'length_measurement', 'fit_status',
                'measured_by', 'diameter_deviation'
            ],
            order_by='measurement_timestamp desc',
            limit=20
        )
        
        return history

    @frappe.whitelist()
    def calculate_fit_analysis(self):
        """Calculate comprehensive fit analysis."""
        if not frappe.has_permission(self.doctype, "write"):
            frappe.throw(_("No permission to calculate fit analysis"))
        
        self._calculate_tolerance_analysis()
        self._update_measurement_metadata()
        
        analysis = {
            'fit_status': self.fit_status,
            'diameter_deviation': self.diameter_deviation,
            'fit_percentage': self.fit_percentage,
            'recommendations': self.recommendations
        }
        
        return analysis
