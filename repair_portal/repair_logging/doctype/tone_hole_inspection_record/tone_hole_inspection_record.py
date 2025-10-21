# Path: repair_portal/repair_logging/doctype/tone_hole_inspection_record/tone_hole_inspection_record.py
# Date: 2025-01-14
# Version: 2.0.0
# Description: Production-ready tone hole inspection tracking with detailed assessment and audit compliance
# Dependencies: frappe, frappe.model.document, frappe.utils

import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


class ToneHoleInspectionRecord(Document):
    """
    Tone Hole Inspection Record: Detailed documentation of tone hole conditions and inspection results.
    Critical for ensuring proper seal and acoustic performance.
    """

    def validate(self):
        """Validate tone hole inspection data with comprehensive requirements."""
        self._validate_required_fields()
        self._validate_tone_hole_data()
        self._validate_inspection_criteria()
        self._validate_measurement_values()
        self._validate_inspector_permissions()

    def before_insert(self):
        """Set defaults and validate inspection setup."""
        self._set_inspection_timestamp()
        self._normalize_inspection_data()
        self._validate_hole_numbering()
        self._log_inspection_audit()

    def before_save(self):
        """Update calculations and validations before saving."""
        self._calculate_condition_scores()
        self._update_inspection_metadata()
        self._validate_inspection_consistency()

    def on_submit(self):
        """Process inspection completion with proper validation."""
        self._validate_inspection_completion()
        self._update_instrument_condition()
        self._check_maintenance_requirements()
        self._generate_inspection_recommendations()

    def _validate_required_fields(self):
        """Validate all required inspection fields are present."""
        required_fields = ["tone_hole_number", "visual_status"]
        missing = [field for field in required_fields if not self.get(field)]
        if missing:
            frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))

    def _validate_tone_hole_data(self):
        """Validate tone hole identification and numbering."""
        if self.tone_hole_number:
            hole_num = str(self.tone_hole_number).strip()

            # Validate hole number format
            if not hole_num:
                frappe.throw(_("Tone hole number cannot be empty"))

            # Check for valid hole numbering (1-17 for most clarinets, plus special holes)
            if hole_num.isdigit():
                hole_int = int(hole_num)
                if hole_int < 1 or hole_int > 24:
                    frappe.msgprint(
                        _("Warning: Tone hole number {0} is outside typical range (1-24)").format(hole_int)
                    )
            elif hole_num.upper() not in ["THUMB", "REGISTER", "SPEAKER", "VENT"]:
                frappe.msgprint(_("Warning: Non-standard tone hole identifier: {0}").format(hole_num))

    def _validate_inspection_criteria(self):
        """Validate inspection criteria and status values."""
        # Validate visual status
        valid_visual_status = [
            "Excellent",
            "Good",
            "Fair",
            "Poor",
            "Damaged",
            "Cracked",
            "Chipped",
            "Worn",
            "Debris Present",
            "Needs Cleaning",
        ]

        if self.visual_status and self.visual_status not in valid_visual_status:
            frappe.throw(
                _("Invalid visual status: {0}. Valid options are: {1}").format(
                    self.visual_status, ", ".join(valid_visual_status)
                )
            )

        # Validate seal quality if specified
        if self.seal_quality:
            valid_seal_quality = ["Excellent", "Good", "Fair", "Poor", "No Seal", "Leaking"]
            if self.seal_quality not in valid_seal_quality:
                frappe.throw(_("Invalid seal quality: {0}").format(self.seal_quality))

        # Validate condition rating
        if self.condition_rating:
            rating = flt(self.condition_rating)
            if rating < 1 or rating > 10:
                frappe.throw(_("Condition rating must be between 1 and 10"))

    def _validate_measurement_values(self):
        """Validate measurement values for reasonableness."""
        # Validate diameter measurements
        if self.hole_diameter:
            diameter = flt(self.hole_diameter)
            if diameter <= 0:
                frappe.throw(_("Hole diameter must be positive"))
            if diameter > 20:  # 20mm is very large for tone holes
                frappe.throw(_("Hole diameter {0}mm seems unreasonably large").format(diameter))
            if diameter < 2:  # 2mm is very small for tone holes
                frappe.msgprint(_("Warning: Hole diameter {0}mm is unusually small").format(diameter))

        # Validate height measurements
        if self.chimney_height:
            height = flt(self.chimney_height)
            if height < 0:
                frappe.throw(_("Chimney height cannot be negative"))
            if height > 15:  # 15mm is very tall for chimneys
                frappe.msgprint(_("Warning: Chimney height {0}mm is unusually tall").format(height))

        # Validate wall thickness if measured
        if self.wall_thickness:
            thickness = flt(self.wall_thickness)
            if thickness <= 0:
                frappe.throw(_("Wall thickness must be positive"))
            if thickness > 5:  # 5mm is very thick
                frappe.msgprint(_("Warning: Wall thickness {0}mm is unusually thick").format(thickness))

    def _validate_inspector_permissions(self):
        """Validate inspector has appropriate permissions for tone hole inspections."""
        if self.inspected_by:
            # Verify inspector exists and is active
            inspector_data = frappe.db.get_value("User", self.inspected_by, ["enabled", "full_name"])

            if not inspector_data or not inspector_data[0]:
                frappe.throw(_("Inspector {0} is not active in the system.").format(self.inspected_by))

            # Check for appropriate inspection roles
            required_roles = ["Technician", "Quality Inspector", "Repair Specialist", "System Manager"]
            user_roles = frappe.get_roles(self.inspected_by)

            if not any(role in user_roles for role in required_roles):
                frappe.throw(
                    _("User {0} does not have appropriate permissions for tone hole inspections.").format(
                        self.inspected_by
                    )
                )

    def _set_inspection_timestamp(self):
        """Set inspection timestamp if not specified."""
        if not self.inspection_timestamp:
            self.inspection_timestamp = now_datetime()

    def _normalize_inspection_data(self):
        """Normalize and structure inspection data."""
        # Create structured inspection summary
        inspection_summary = {
            "tone_hole_number": self.tone_hole_number,
            "visual_status": self.visual_status,
            "seal_quality": self.seal_quality,
            "condition_rating": self.condition_rating,
            "diameter": self.hole_diameter,
            "chimney_height": self.chimney_height,
            "wall_thickness": self.wall_thickness,
            "inspector": self.inspected_by,
            "timestamp": str(self.inspection_timestamp),
        }

        # Store inspection metadata
        if not self.inspection_metadata:
            self.inspection_metadata = json.dumps(inspection_summary, indent=2, default=str)

    def _validate_hole_numbering(self):
        """Validate hole numbering consistency within instrument."""
        if not (self.tone_hole_number and hasattr(self, "parent")):
            return

        # Check for duplicate hole numbers in the same inspection
        if self.parent and self.parenttype:
            existing_holes = frappe.get_all(
                self.doctype,
                filters={
                    "parent": self.parent,
                    "parenttype": self.parenttype,
                    "tone_hole_number": self.tone_hole_number,
                    "name": ["!=", self.name or ""],
                },
                fields=["name"],
            )

            if existing_holes:
                frappe.throw(
                    _("Tone hole number {0} already exists in this inspection").format(self.tone_hole_number)
                )

    def _calculate_condition_scores(self):
        """Calculate comprehensive condition scores and metrics."""
        scores = []

        # Visual status scoring
        visual_scores = {
            "Excellent": 10,
            "Good": 8,
            "Fair": 6,
            "Poor": 4,
            "Damaged": 2,
            "Cracked": 2,
            "Chipped": 3,
            "Worn": 5,
            "Debris Present": 6,
            "Needs Cleaning": 7,
        }

        if self.visual_status and self.visual_status in visual_scores:
            visual_score = visual_scores[self.visual_status]
            scores.append(visual_score)

        # Seal quality scoring
        seal_scores = {"Excellent": 10, "Good": 8, "Fair": 6, "Poor": 4, "No Seal": 1, "Leaking": 2}

        if self.seal_quality and self.seal_quality in seal_scores:
            seal_score = seal_scores[self.seal_quality]
            scores.append(seal_score)

        # Calculate overall condition score
        if scores:
            self.calculated_condition_score = sum(scores) / len(scores)

        # Use manual rating if provided, otherwise use calculated
        if not self.condition_rating and self.calculated_condition_score:
            self.condition_rating = self.calculated_condition_score

    def _update_inspection_metadata(self):
        """Update inspection metadata with current values."""
        try:
            metadata = json.loads(self.inspection_metadata or "{}")
            metadata.update(
                {
                    "last_modified": str(now_datetime()),
                    "modified_by": frappe.session.user,
                    "calculated_score": self.calculated_condition_score,
                    "final_rating": self.condition_rating,
                }
            )
            self.inspection_metadata = json.dumps(metadata, indent=2, default=str)
        except json.JSONDecodeError:
            # Reset metadata if corrupted
            self._normalize_inspection_data()

    def _validate_inspection_consistency(self):
        """Validate inspection data consistency."""
        # Check for logical consistency between visual status and condition rating
        if self.visual_status and self.condition_rating:
            rating = flt(self.condition_rating)

            if self.visual_status in ["Excellent", "Good"] and rating < 6:
                frappe.msgprint(
                    _("Warning: Good visual status but low condition rating ({0})").format(rating)
                )
            elif self.visual_status in ["Damaged", "Cracked"] and rating > 4:
                frappe.msgprint(
                    _("Warning: Damaged visual status but high condition rating ({0})").format(rating)
                )

    def _validate_inspection_completion(self):
        """Validate inspection is complete before submission."""
        if not self.inspected_by:
            frappe.throw(_("Inspector field is required for submission"))

        if not self.inspection_timestamp:
            frappe.throw(_("Inspection timestamp is required for submission"))

        if not self.condition_rating:
            frappe.throw(_("Condition rating is required for submission"))

        # Require photo for poor conditions
        if self.visual_status in ["Poor", "Damaged", "Cracked", "Chipped"] and not self.photo:
            frappe.throw(_("Photo documentation is required for damaged or poor condition tone holes"))

    def _update_instrument_condition(self):
        """Update instrument condition tracking with inspection results."""
        if not (self.parent and self.parenttype):
            return

        try:
            # Log inspection result for instrument history
            inspection_record = {
                "inspection_id": self.name,
                "tone_hole_number": self.tone_hole_number,
                "visual_status": self.visual_status,
                "seal_quality": self.seal_quality,
                "condition_rating": self.condition_rating,
                "inspector": self.inspected_by,
                "timestamp": str(self.inspection_timestamp),
            }

            frappe.logger("tone_hole_inspection_history").info(
                {
                    "action": "inspection_recorded",
                    "parent_document": self.parent,
                    "parent_type": self.parenttype,
                    "inspection_data": inspection_record,
                }
            )

        except Exception as e:
            frappe.log_error(f"Failed to update instrument condition: {str(e)}")

    def _check_maintenance_requirements(self):
        """Check maintenance requirements and generate alerts."""
        maintenance_needed = False
        alerts = []

        # Check for immediate maintenance needs
        if self.visual_status in ["Damaged", "Cracked", "Chipped"]:
            maintenance_needed = True
            alerts.append(
                f"Tone hole {self.tone_hole_number}: {self.visual_status} - requires immediate attention"
            )

        if self.seal_quality in ["No Seal", "Leaking"]:
            maintenance_needed = True
            alerts.append(f"Tone hole {self.tone_hole_number}: Seal problem - affects playability")

        if self.condition_rating and flt(self.condition_rating) <= 3:
            maintenance_needed = True
            alerts.append(
                f"Tone hole {self.tone_hole_number}: Poor condition (rating {self.condition_rating})"
            )

        # Generate alerts if needed
        if maintenance_needed and alerts:
            alert_message = "Maintenance Required:\n" + "\n".join(alerts)
            frappe.msgprint(alert_message, alert=True)

            # Log maintenance alert
            frappe.logger("maintenance_alerts").warning(
                {
                    "action": "tone_hole_maintenance_required",
                    "tone_hole_number": self.tone_hole_number,
                    "visual_status": self.visual_status,
                    "seal_quality": self.seal_quality,
                    "condition_rating": self.condition_rating,
                    "inspector": self.inspected_by,
                    "alerts": alerts,
                }
            )

    def _generate_inspection_recommendations(self):
        """Generate inspection recommendations based on findings."""
        if not self.recommendations:
            recommendations = []

            # Visual status recommendations
            if self.visual_status == "Needs Cleaning":
                recommendations.append("Clean tone hole thoroughly before further assessment")
            elif self.visual_status == "Debris Present":
                recommendations.append("Remove debris and inspect for underlying damage")
            elif self.visual_status in ["Damaged", "Cracked"]:
                recommendations.append("Evaluate for repair or replacement")
                recommendations.append("Consult specialist for structural integrity assessment")
            elif self.visual_status == "Chipped":
                recommendations.append("Sand or file smooth if minor, consider replacement if significant")
            elif self.visual_status == "Worn":
                recommendations.append("Monitor for progression, may need preventive maintenance")

            # Seal quality recommendations
            if self.seal_quality in ["No Seal", "Leaking"]:
                recommendations.append("Check pad condition and adjustment")
                recommendations.append("Verify tone hole levelness and key regulation")
            elif self.seal_quality == "Poor":
                recommendations.append("Adjust key regulation or replace pad")

            # Condition rating recommendations
            if self.condition_rating and flt(self.condition_rating) <= 4:
                recommendations.append("Schedule priority maintenance")
                recommendations.append("Consider impact on overall instrument performance")

            if recommendations:
                self.recommendations = "\n".join(recommendations)

    def _log_inspection_audit(self):
        """Log tone hole inspection for audit compliance."""
        frappe.logger("tone_hole_inspection_audit").info(
            {
                "action": "tone_hole_inspection",
                "tone_hole_number": self.tone_hole_number,
                "visual_status": self.visual_status,
                "seal_quality": self.seal_quality,
                "condition_rating": self.condition_rating,
                "diameter": self.hole_diameter,
                "chimney_height": self.chimney_height,
                "inspected_by": self.inspected_by,
                "parent_document": getattr(self, "parent", None),
                "user": frappe.session.user,
                "timestamp": str(self.inspection_timestamp),
            }
        )
