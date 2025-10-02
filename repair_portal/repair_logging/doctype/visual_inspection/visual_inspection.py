# Path: repair_portal/repair_logging/doctype/visual_inspection/visual_inspection.py
# Date: 2025-01-14
# Version: 2.0.0
# Description: Production-ready visual inspection tracking with standardized assessment and audit compliance
# Dependencies: frappe, frappe.model.document, frappe.utils

import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, now_datetime


class VisualInspection(Document):
    """
    Visual Inspection: Comprehensive visual assessment of instrument condition with standardized criteria.
    Essential for establishing baseline condition and tracking deterioration over time.
    """

    def validate(self):
        """Validate visual inspection data with comprehensive business rules."""
        self._validate_required_fields()
        self._validate_instrument_reference()
        self._validate_inspection_criteria()
        self._validate_condition_ratings()
        self._validate_inspector_permissions()

    def before_insert(self):
        """Set defaults and validate inspection setup."""
        self._set_inspection_timestamp()
        self._normalize_inspection_data()
        self._validate_inspection_scope()
        self._log_inspection_audit()

    def before_save(self):
        """Update calculations and validations before saving."""
        self._calculate_overall_condition()
        self._update_inspection_metadata()
        self._validate_inspection_consistency()

    def on_submit(self):
        """Process inspection completion with proper validation."""
        self._validate_inspection_completion()
        self._update_instrument_condition()
        self._check_maintenance_alerts()
        self._generate_inspection_report()

    def _validate_required_fields(self):
        """Validate all required inspection fields are present."""
        required_fields = ["inspection_type", "inspector"]
        missing = [field for field in required_fields if not self.get(field)]
        if missing:
            frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))

    def _validate_instrument_reference(self):
        """Validate instrument reference exists and is accessible."""
        if self.instrument_profile:
            if not frappe.db.exists('Instrument Profile', self.instrument_profile):
                frappe.throw(_("Instrument Profile {0} does not exist").format(self.instrument_profile))
            
            if not frappe.has_permission("Instrument Profile", "read", self.instrument_profile):
                frappe.throw(_("No permission to access instrument {0}").format(self.instrument_profile))
            
            # Get instrument details for validation context
            instrument_data = frappe.db.get_value('Instrument Profile', self.instrument_profile, 
                ['instrument_type', 'instrument_model', 'serial_number'], as_dict=True)
            
            if instrument_data:
                self.instrument_type = instrument_data.instrument_type
                self.instrument_model = instrument_data.instrument_model

    def _validate_inspection_criteria(self):
        """Validate inspection criteria and assessment methods."""
        # Validate inspection type
        valid_inspection_types = [
            'Initial Assessment',
            'Routine Inspection',
            'Pre-Repair Assessment',
            'Post-Repair Verification',
            'Quality Control',
            'Damage Assessment',
            'Warranty Evaluation',
            'Final Inspection'
        ]
        
        if self.inspection_type and self.inspection_type not in valid_inspection_types:
            frappe.throw(_("Invalid inspection type: {0}. Valid options are: {1}").format(
                self.inspection_type, ', '.join(valid_inspection_types)))
        
        # Validate inspection method
        if self.inspection_method:
            valid_methods = [
                'Visual Only',
                'Visual + Basic Tools',
                'Comprehensive Assessment',
                'Photographic Documentation',
                'Video Documentation',
                'Microscopic Examination'
            ]
            
            if self.inspection_method not in valid_methods:
                frappe.throw(_("Invalid inspection method: {0}").format(self.inspection_method))

    def _validate_condition_ratings(self):
        """Validate condition ratings are within acceptable ranges."""
        rating_fields = [
            'overall_condition_rating',
            'body_condition_rating',
            'key_condition_rating',
            'pad_condition_rating',
            'spring_condition_rating'
        ]
        
        for field in rating_fields:
            if self.get(field):
                rating = flt(self.get(field))
                if rating < 1 or rating > 10:
                    frappe.throw(_("{0} must be between 1 and 10").format(
                        field.replace('_', ' ').title()))
        
        # Validate condition status values
        if self.condition_status:
            valid_status = [
                'Excellent',
                'Very Good', 
                'Good',
                'Fair',
                'Poor',
                'Very Poor',
                'Requires Immediate Attention'
            ]
            
            if self.condition_status not in valid_status:
                frappe.throw(_("Invalid condition status: {0}").format(self.condition_status))

    def _validate_inspector_permissions(self):
        """Validate inspector has appropriate permissions for visual inspections."""
        if self.inspector:
            # Verify inspector exists and is active
            inspector_data = frappe.db.get_value('User', self.inspector, ['enabled', 'full_name'])
            
            if not inspector_data or not inspector_data[0]:
                frappe.throw(_('Inspector {0} is not active in the system.').format(self.inspector))
            
            # Check for appropriate inspection roles
            required_roles = ['Technician', 'Quality Inspector', 'Repair Specialist', 'Inspector', 'System Manager']
            user_roles = frappe.get_roles(self.inspector)
            
            if not any(role in user_roles for role in required_roles):
                frappe.throw(_('User {0} does not have appropriate permissions for visual inspections.').format(self.inspector))

    def _set_inspection_timestamp(self):
        """Set inspection timestamp if not specified."""
        if not self.inspection_date:
            self.inspection_date = getdate()
        
        if not self.inspection_time:
            self.inspection_time = now_datetime()

    def _normalize_inspection_data(self):
        """Normalize and structure inspection data."""
        # Create structured inspection summary
        inspection_summary = {
            'instrument_profile': self.instrument_profile,
            'inspection_type': self.inspection_type,
            'inspection_method': self.inspection_method,
            'inspector': self.inspector,
            'inspection_date': str(self.inspection_date),
            'inspection_time': str(self.inspection_time),
            'overall_condition': self.overall_condition_rating,
            'condition_status': self.condition_status
        }
        
        # Store inspection metadata
        if not self.inspection_metadata:
            self.inspection_metadata = json.dumps(inspection_summary, indent=2, default=str)

    def _validate_inspection_scope(self):
        """Validate inspection scope and completeness."""
        # Check if inspection scope is comprehensive for type
        if (self.inspection_type in ['Pre-Repair Assessment', 'Post-Repair Verification', 'Quality Control'] and 
            not (self.body_condition_rating and self.key_condition_rating)):
            frappe.msgprint(_("Warning: {0} typically requires detailed component ratings").format(self.inspection_type))

    def _calculate_overall_condition(self):
        """Calculate overall condition rating from component ratings."""
        # Collect all component ratings
        component_ratings = [
            self.body_condition_rating,
            self.key_condition_rating,
            self.pad_condition_rating,
            self.spring_condition_rating
        ]
        
        # Filter out None/empty values and convert to float
        valid_ratings = [flt(rating) for rating in component_ratings if rating]
        
        if valid_ratings:
            # Calculate weighted average (can be customized by instrument type)
            calculated_overall = sum(valid_ratings) / len(valid_ratings)
            
            # Use calculated value if overall not manually set
            if not self.overall_condition_rating:
                self.overall_condition_rating = round(calculated_overall, 1)
            
            # Determine condition status based on rating
            if not self.condition_status:
                self.condition_status = self._get_condition_status_from_rating(calculated_overall)

    def _get_condition_status_from_rating(self, rating):
        """Convert numeric rating to condition status."""
        rating = flt(rating)
        
        if rating >= 9:
            return 'Excellent'
        elif rating >= 8:
            return 'Very Good'
        elif rating >= 7:
            return 'Good'
        elif rating >= 5:
            return 'Fair'
        elif rating >= 3:
            return 'Poor'
        elif rating >= 1:
            return 'Very Poor'
        else:
            return 'Requires Immediate Attention'

    def _update_inspection_metadata(self):
        """Update inspection metadata with current values."""
        try:
            metadata = json.loads(self.inspection_metadata or '{}')
            metadata.update({
                'last_modified': str(now_datetime()),
                'modified_by': frappe.session.user,
                'calculated_overall': self.overall_condition_rating,
                'condition_status': self.condition_status,
                'findings_count': len((self.findings or '').split('\n')) if self.findings else 0,
                'recommendations_count': len((self.recommendations or '').split('\n')) if self.recommendations else 0
            })
            self.inspection_metadata = json.dumps(metadata, indent=2, default=str)
        except json.JSONDecodeError:
            # Reset metadata if corrupted
            self._normalize_inspection_data()

    def _validate_inspection_consistency(self):
        """Validate inspection data consistency."""
        # Check for logical consistency between ratings and status
        if self.overall_condition_rating and self.condition_status:
            rating = flt(self.overall_condition_rating)
            expected_status = self._get_condition_status_from_rating(rating)
            
            if self.condition_status != expected_status:
                frappe.msgprint(_("Warning: Condition status '{0}' may not match rating {1} (Expected: {2})").format(
                    self.condition_status, rating, expected_status))
        
        # Check component ratings consistency
        if self.overall_condition_rating:
            overall = flt(self.overall_condition_rating)
            component_ratings = [
                flt(self.body_condition_rating or 0),
                flt(self.key_condition_rating or 0),
                flt(self.pad_condition_rating or 0),
                flt(self.spring_condition_rating or 0)
            ]
            
            valid_components = [r for r in component_ratings if r > 0]
            if valid_components:
                avg_components = sum(valid_components) / len(valid_components)
                
                if abs(overall - avg_components) > 2:
                    frappe.msgprint(_("Warning: Overall rating {0} differs significantly from component average {1}").format(
                        overall, round(avg_components, 1)))

    def _validate_inspection_completion(self):
        """Validate inspection is complete before submission."""
        if not self.inspector:
            frappe.throw(_("Inspector field is required for submission"))
        
        if not self.inspection_date:
            frappe.throw(_("Inspection date is required for submission"))
        
        if not self.overall_condition_rating:
            frappe.throw(_("Overall condition rating is required for submission"))
        
        # Require findings for poor conditions
        if self.condition_status in ['Poor', 'Very Poor', 'Requires Immediate Attention'] and not self.findings:
            frappe.throw(_("Detailed findings are required for poor condition ratings"))
        
        # Require recommendations for issues found
        if self.findings and not self.recommendations:
            frappe.msgprint(_("Consider adding recommendations based on findings"))

    def _update_instrument_condition(self):
        """Update instrument condition tracking with inspection results."""
        if not self.instrument_profile:
            return
            
        try:
            instrument = frappe.get_doc('Instrument Profile', self.instrument_profile)
            
            # Update condition fields if they exist
            if hasattr(instrument, 'last_inspection_date'):
                instrument.db_set('last_inspection_date', self.inspection_date)
            
            if hasattr(instrument, 'last_inspection_rating'):
                instrument.db_set('last_inspection_rating', self.overall_condition_rating)
            
            if hasattr(instrument, 'condition_status'):
                instrument.db_set('condition_status', self.condition_status)
            
            # Log inspection result for instrument history
            inspection_record = {
                'inspection_id': self.name,
                'inspection_type': self.inspection_type,
                'inspector': self.inspector,
                'overall_rating': self.overall_condition_rating,
                'condition_status': self.condition_status,
                'inspection_date': str(self.inspection_date)
            }
            
            frappe.logger("instrument_inspection_history").info({
                "action": "inspection_completed",
                "instrument_profile": self.instrument_profile,
                "inspection_data": inspection_record
            })
            
        except Exception as e:
            frappe.log_error(f"Failed to update instrument condition: {str(e)}")

    def _check_maintenance_alerts(self):
        """Check for maintenance alerts based on inspection results."""
        alerts = []
        
        # Check overall condition
        if self.overall_condition_rating and flt(self.overall_condition_rating) <= 4:
            alerts.append(f"Overall condition rating {self.overall_condition_rating} indicates need for maintenance")
        
        # Check specific components
        if self.pad_condition_rating and flt(self.pad_condition_rating) <= 3:
            alerts.append("Pad condition requires immediate attention")
        
        if self.spring_condition_rating and flt(self.spring_condition_rating) <= 3:
            alerts.append("Spring condition requires maintenance")
        
        if self.key_condition_rating and flt(self.key_condition_rating) <= 3:
            alerts.append("Key mechanism requires adjustment or repair")
        
        # Check condition status
        if self.condition_status in ['Poor', 'Very Poor', 'Requires Immediate Attention']:
            alerts.append(f"Condition status '{self.condition_status}' requires prompt action")
        
        # Generate alerts if needed
        if alerts:
            alert_message = "Maintenance Alerts:\n" + "\n".join(alerts)
            frappe.msgprint(alert_message, alert=True)
            
            # Log maintenance alerts
            frappe.logger("maintenance_alerts").warning({
                "action": "visual_inspection_maintenance_alerts",
                "instrument_profile": self.instrument_profile,
                "inspection_type": self.inspection_type,
                "overall_rating": self.overall_condition_rating,
                "condition_status": self.condition_status,
                "alerts": alerts,
                "inspector": self.inspector
            })

    def _generate_inspection_report(self):
        """Generate inspection recommendations based on findings."""
        if not self.recommendations and (self.findings or self.overall_condition_rating):
            recommendations = []
            
            # Overall condition recommendations
            if self.overall_condition_rating:
                rating = flt(self.overall_condition_rating)
                
                if rating <= 3:
                    recommendations.append("Schedule comprehensive repair assessment")
                    recommendations.append("Consider instrument replacement evaluation")
                elif rating <= 5:
                    recommendations.append("Schedule preventive maintenance")
                    recommendations.append("Monitor condition closely")
                elif rating <= 7:
                    recommendations.append("Routine maintenance recommended")
                
            # Component-specific recommendations
            if self.pad_condition_rating and flt(self.pad_condition_rating) <= 4:
                recommendations.append("Pad replacement or adjustment needed")
            
            if self.spring_condition_rating and flt(self.spring_condition_rating) <= 4:
                recommendations.append("Spring tension adjustment or replacement")
            
            if self.key_condition_rating and flt(self.key_condition_rating) <= 4:
                recommendations.append("Key mechanism regulation required")
            
            # Set recommendations if generated
            if recommendations and not self.recommendations:
                self.recommendations = '\n'.join(recommendations)

    def _log_inspection_audit(self):
        """Log visual inspection for audit compliance."""
        frappe.logger("visual_inspection_audit").info({
            "action": "visual_inspection",
            "instrument_profile": self.instrument_profile,
            "inspection_type": self.inspection_type,
            "inspection_method": self.inspection_method,
            "inspector": self.inspector,
            "overall_rating": self.overall_condition_rating,
            "condition_status": self.condition_status,
            "body_rating": self.body_condition_rating,
            "key_rating": self.key_condition_rating,
            "pad_rating": self.pad_condition_rating,
            "spring_rating": self.spring_condition_rating,
            "user": frappe.session.user,
            "timestamp": str(self.inspection_time)
        })

    @frappe.whitelist()
    def get_inspection_history(self):
        """Get inspection history for this instrument."""
        if not frappe.has_permission(self.doctype, "read"):
            frappe.throw(_("No permission to view inspection history"))
        
        if not self.instrument_profile:
            return []
        
        history = frappe.get_all(self.doctype,
            filters={
                'instrument_profile': self.instrument_profile,
                'docstatus': ['!=', 2]
            },
            fields=[
                'name', 'inspection_date', 'inspection_type', 'inspector',
                'overall_condition_rating', 'condition_status', 'findings'
            ],
            order_by='inspection_date desc',
            limit=20
        )
        
        return history

    @frappe.whitelist()
    def calculate_condition_trends(self):
        """Calculate condition trends over time."""
        if not frappe.has_permission(self.doctype, "read"):
            frappe.throw(_("No permission to calculate trends"))
        
        if not self.instrument_profile:
            return {}
        
        # Get recent inspection ratings
        recent_inspections = frappe.get_all(self.doctype,
            filters={
                'instrument_profile': self.instrument_profile,
                'docstatus': ['!=', 2],
                'overall_condition_rating': ['is', 'set']
            },
            fields=['inspection_date', 'overall_condition_rating'],
            order_by='inspection_date desc',
            limit=10
        )
        
        if len(recent_inspections) < 2:
            return {'trend': 'insufficient_data'}
        
        # Calculate trend
        ratings = [flt(insp.overall_condition_rating) for insp in recent_inspections]
        
        if len(ratings) >= 3:
            recent_avg = sum(ratings[:3]) / 3
            older_avg = sum(ratings[3:6]) / min(3, len(ratings[3:6])) if len(ratings) > 3 else ratings[-1]
            
            trend_direction = 'improving' if recent_avg > older_avg else 'declining' if recent_avg < older_avg else 'stable'
        else:
            trend_direction = 'improving' if ratings[0] > ratings[1] else 'declining' if ratings[0] < ratings[1] else 'stable'
        
        return {
            'trend': trend_direction,
            'current_rating': ratings[0] if ratings else None,
            'previous_rating': ratings[1] if len(ratings) > 1 else None,
            'inspection_count': len(recent_inspections)
        }
