# Path: repair_portal/repair_logging/doctype/pad_condition/pad_condition.py
# Date: 2025-01-14
# Version: 2.0.0
# Description: Production-ready pad condition assessment with standardized grading, validation, and audit compliance
# Dependencies: frappe, frappe.model.document, frappe.utils


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


class PadCondition(Document):
    """
    Pad Condition: Assess and track clarinet pad conditions with standardized grading.
    """

    def validate(self):
        """Validate pad condition assessment with comprehensive business rules."""
        self._validate_required_fields()
        self._validate_pad_identification()
        self._validate_condition_ratings()
        self._validate_assessment_criteria()
        self._validate_technician_qualifications()

    def before_insert(self):
        """Set defaults and process assessment data."""
        self._set_assessment_timestamp()
        self._calculate_overall_condition()
        self._set_recommended_actions()
        self._log_assessment_audit()

    def before_save(self):
        """Update calculations and validations before saving."""
        self._update_condition_calculations()
        self._validate_assessment_consistency()

    def on_submit(self):
        """Process assessment completion with proper validation."""
        self._validate_assessment_completion()
        self._update_instrument_pad_status()
        self._create_maintenance_recommendations()

    def _validate_required_fields(self):
        """Validate all required fields are present."""
        required_fields = ["pad_location", "condition_rating"]
        missing = [field for field in required_fields if not self.get(field)]
        if missing:
            frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))

    def _validate_pad_identification(self):
        """Validate pad identification and location data."""
        # Validate pad location format
        valid_locations = [
            "Upper Joint - Tone Hole 1",
            "Upper Joint - Tone Hole 2",
            "Upper Joint - Tone Hole 3",
            "Upper Joint - Tone Hole 4",
            "Upper Joint - Tone Hole 5",
            "Upper Joint - Tone Hole 6",
            "Lower Joint - Tone Hole 7",
            "Lower Joint - Tone Hole 8",
            "Lower Joint - Tone Hole 9",
            "Lower Joint - Tone Hole 10",
            "Lower Joint - Tone Hole 11",
            "Lower Joint - Tone Hole 12",
            "Bell - Tone Hole 13",
            "Register Key",
            "Thumb Hole",
            "Other",
        ]

        if self.pad_location and self.pad_location not in valid_locations:
            frappe.msgprint(_("Warning: Non-standard pad location: {0}").format(self.pad_location))

        # Validate instrument reference
        if self.instrument_reference:
            if not frappe.db.exists("Instrument Profile", self.instrument_reference):
                frappe.throw(_("Instrument reference {0} does not exist").format(self.instrument_reference))

            # Check instrument type compatibility
            instrument_type = frappe.db.get_value(
                "Instrument Profile", self.instrument_reference, "instrument_type"
            )
            if instrument_type and "clarinet" not in instrument_type.lower():
                frappe.msgprint(_("Warning: Pad assessment being performed on non-clarinet instrument"))

    def _validate_condition_ratings(self):
        """Validate condition ratings are within acceptable ranges."""
        # Main condition rating (1-5 scale)
        if self.condition_rating and (flt(self.condition_rating) < 1 or flt(self.condition_rating) > 5):
            frappe.throw(_("Condition rating must be between 1 and 5"))

        # Individual assessment criteria (0-10 scale)
        criteria_fields = [
            "sealing_effectiveness",
            "pad_wear_level",
            "spring_tension",
            "key_alignment",
            "moisture_damage",
            "surface_condition",
        ]

        for field in criteria_fields:
            value = self.get(field)
            if value and (flt(value) < 0 or flt(value) > 10):
                frappe.throw(_("{0} rating must be between 0 and 10").format(field.replace("_", " ").title()))

    def _validate_assessment_criteria(self):
        """Validate assessment criteria consistency and logic."""
        # Check for logical inconsistencies
        if self.condition_rating and self.sealing_effectiveness:
            if flt(self.condition_rating) >= 4 and flt(self.sealing_effectiveness) <= 3:
                frappe.msgprint(_("Warning: High condition rating with poor sealing effectiveness"))

            if flt(self.condition_rating) <= 2 and flt(self.sealing_effectiveness) >= 8:
                frappe.msgprint(_("Warning: Low condition rating with excellent sealing effectiveness"))

        # Validate replacement recommendation logic
        if self.condition_rating and flt(self.condition_rating) <= 2 and not self.requires_replacement:
            frappe.msgprint(_("Warning: Poor condition rating may require replacement consideration"))

    def _validate_technician_qualifications(self):
        """Validate technician is qualified for pad assessments."""
        if self.assessed_by:
            # Verify technician exists and is active
            technician_data = frappe.db.get_value("User", self.assessed_by, ["enabled", "full_name"])

            if not technician_data or not technician_data[0]:
                frappe.throw(_("Technician {0} is not active in the system.").format(self.assessed_by))

            # Check for pad assessment certification
            required_roles = ["Technician", "Pad Specialist", "Clarinet Technician", "System Manager"]
            user_roles = frappe.get_roles(self.assessed_by)

            if not any(role in user_roles for role in required_roles):
                frappe.msgprint(
                    _("Warning: User {0} may not be certified for pad assessments.").format(self.assessed_by)
                )

    def _set_assessment_timestamp(self):
        """Set assessment timestamp if not specified."""
        if not self.assessment_date:
            self.assessment_date = now_datetime()

    def _calculate_overall_condition(self):
        """Calculate overall condition score based on individual criteria."""
        criteria_weights = {
            "sealing_effectiveness": 0.3,
            "pad_wear_level": 0.2,
            "spring_tension": 0.15,
            "key_alignment": 0.15,
            "moisture_damage": 0.1,
            "surface_condition": 0.1,
        }

        weighted_score = 0
        total_weight = 0

        for field, weight in criteria_weights.items():
            value = self.get(field)
            if value is not None:
                weighted_score += flt(value) * weight
                total_weight += weight

        if total_weight > 0:
            # Convert 0-10 scale to 1-5 scale
            overall_score = (weighted_score / total_weight) / 2 + 0.5
            self.calculated_condition_score = round(overall_score, 2)

            # If no manual rating provided, use calculated score
            if not self.condition_rating:
                self.condition_rating = round(overall_score)

    def _set_recommended_actions(self):
        """Set recommended actions based on condition assessment."""
        actions = []

        if self.condition_rating:
            rating = flt(self.condition_rating)

            if rating <= 2:
                actions.append("Replace pad immediately")
                self.requires_replacement = 1
                self.urgency_level = "High"
            elif rating <= 3:
                actions.append("Schedule pad replacement soon")
                self.urgency_level = "Medium"
            elif rating == 4:
                actions.append("Monitor pad condition closely")
                self.urgency_level = "Low"
            else:
                actions.append("Pad in good condition")
                self.urgency_level = "None"

        # Specific criteria recommendations
        if self.sealing_effectiveness and flt(self.sealing_effectiveness) <= 3:
            actions.append("Check key adjustment and seat alignment")

        if self.spring_tension and flt(self.spring_tension) <= 4:
            actions.append("Adjust or replace key spring")

        if self.moisture_damage and flt(self.moisture_damage) <= 3:
            actions.append("Address moisture control and cleaning")

        if actions:
            self.recommended_actions = "; ".join(actions)

    def _update_condition_calculations(self):
        """Update condition calculations and derived fields."""
        # Recalculate overall condition
        self._calculate_overall_condition()

        # Update recommended actions
        self._set_recommended_actions()

        # Update assessment completeness
        criteria_fields = [
            "sealing_effectiveness",
            "pad_wear_level",
            "spring_tension",
            "key_alignment",
            "moisture_damage",
            "surface_condition",
        ]

        completed_criteria = sum(1 for field in criteria_fields if self.get(field) is not None)
        self.assessment_completeness = (completed_criteria / len(criteria_fields)) * 100

    def _validate_assessment_consistency(self):
        """Validate assessment data consistency."""
        # Check if manual condition rating significantly differs from calculated
        if self.condition_rating and self.calculated_condition_score:
            difference = abs(flt(self.condition_rating) - flt(self.calculated_condition_score))
            if difference > 1.5:
                frappe.msgprint(_("Warning: Manual rating differs significantly from calculated score"))

    def _validate_assessment_completion(self):
        """Validate assessment is complete before submission."""
        if not self.assessed_by:
            frappe.throw(_("Assessed by field is required for submission"))

        if not self.assessment_date:
            frappe.throw(_("Assessment date is required for submission"))

        if self.requires_replacement and not self.replacement_notes:
            frappe.throw(_("Replacement notes are required when replacement is needed"))

    def _update_instrument_pad_status(self):
        """Update instrument's overall pad status."""
        if self.instrument_reference:
            try:
                # Get all pad conditions for this instrument
                pad_conditions = frappe.get_all(
                    "Pad Condition",
                    filters={"instrument_reference": self.instrument_reference, "docstatus": 1},
                    fields=["condition_rating", "pad_location", "requires_replacement"],
                )

                if pad_conditions:
                    # Calculate overall pad status
                    ratings = [
                        flt(pad["condition_rating"]) for pad in pad_conditions if pad["condition_rating"]
                    ]
                    replacement_needed = any(pad["requires_replacement"] for pad in pad_conditions)

                    if ratings:
                        avg_rating = sum(ratings) / len(ratings)

                        # Update instrument pad status
                        instrument = frappe.get_doc("Instrument Profile", self.instrument_reference)

                        if hasattr(instrument, "pad_condition_average"):
                            instrument.db_set("pad_condition_average", round(avg_rating, 2))

                        if hasattr(instrument, "pads_need_replacement"):
                            instrument.db_set("pads_need_replacement", replacement_needed)

                        # Set overall pad status
                        if hasattr(instrument, "pad_status"):
                            if replacement_needed:
                                status = "Needs Replacement"
                            elif avg_rating >= 4:
                                status = "Good"
                            elif avg_rating >= 3:
                                status = "Fair"
                            else:
                                status = "Poor"

                            instrument.db_set("pad_status", status)

                frappe.logger("pad_assessment").info(
                    {
                        "action": "instrument_pad_status_updated",
                        "instrument": self.instrument_reference,
                        "pad_location": self.pad_location,
                        "condition_rating": self.condition_rating,
                        "requires_replacement": self.requires_replacement,
                    }
                )

            except Exception as e:
                frappe.log_error(f"Failed to update instrument pad status: {str(e)}")

    def _create_maintenance_recommendations(self):
        """Create maintenance recommendations based on assessment."""
        if self.requires_replacement and self.urgency_level in ["High", "Medium"]:
            try:
                # Create maintenance task
                task = frappe.get_doc(
                    {
                        "doctype": "ToDo",
                        "description": f"Pad replacement required: {self.pad_location} on {self.instrument_reference}",
                        "reference_type": self.doctype,
                        "reference_name": self.name,
                        "assigned_by": frappe.session.user,
                        "priority": "High" if self.urgency_level == "High" else "Medium",
                    }
                )
                task.insert()

                frappe.logger("maintenance_tracking").info(
                    {
                        "action": "maintenance_task_created",
                        "task": task.name,
                        "pad_condition": self.name,
                        "urgency": self.urgency_level,
                    }
                )

            except Exception as e:
                frappe.log_error(f"Failed to create maintenance recommendation: {str(e)}")

    def _log_assessment_audit(self):
        """Log pad assessment for audit compliance."""
        frappe.logger("pad_assessment_audit").info(
            {
                "action": "pad_condition_assessed",
                "pad_location": self.pad_location,
                "instrument_reference": self.instrument_reference,
                "condition_rating": self.condition_rating,
                "assessed_by": self.assessed_by,
                "requires_replacement": self.requires_replacement,
                "user": frappe.session.user,
                "timestamp": str(self.assessment_date),
            }
        )

    @frappe.whitelist()
    def recalculate_condition(self):
        """Recalculate condition score and recommendations."""
        if not frappe.has_permission(self.doctype, "write", self.name):
            frappe.throw(_("No permission to recalculate condition"))

        self._calculate_overall_condition()
        self._set_recommended_actions()
        self._update_condition_calculations()
        self.save()

        frappe.logger("pad_assessment").info(
            {
                "action": "condition_recalculated",
                "pad_condition": self.name,
                "new_score": self.calculated_condition_score,
                "user": frappe.session.user,
            }
        )

        return {
            "message": "Condition recalculated successfully",
            "calculated_score": self.calculated_condition_score,
            "recommended_actions": self.recommended_actions,
        }

    @frappe.whitelist()
    def get_replacement_history(self):
        """Get replacement history for this pad location."""
        if not frappe.has_permission(self.doctype, "read"):
            frappe.throw(_("No permission to view replacement history"))

        history = frappe.get_all(
            self.doctype,
            filters={
                "instrument_reference": self.instrument_reference,
                "pad_location": self.pad_location,
                "docstatus": 1,
            },
            fields=["name", "assessment_date", "condition_rating", "assessed_by", "requires_replacement"],
            order_by="assessment_date desc",
            limit=20,
        )

        return history
