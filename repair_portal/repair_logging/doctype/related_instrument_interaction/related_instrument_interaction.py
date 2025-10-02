# Path: repair_portal/repair_logging/doctype/related_instrument_interaction/related_instrument_interaction.py
# Date: 2025-01-14
# Version: 2.0.0
# Description: Production-ready related instrument interaction tracking with cross-reference validation and audit compliance
# Dependencies: frappe, frappe.model.document, frappe.utils

import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class RelatedInstrumentInteraction(Document):
    """
    Related Instrument Interaction: Track interactions between related instruments during repair processes.
    """

    def validate(self):
        """Validate related instrument interaction with comprehensive business rules."""
        self._validate_required_fields()
        self._validate_instrument_references()
        self._validate_relationship_type()
        self._validate_interaction_logic()
        self._validate_user_permissions()

    def before_insert(self):
        """Set defaults and process interaction data."""
        self._set_interaction_timestamp()
        self._normalize_relationship_data()
        self._validate_cross_references()
        self._log_interaction_audit()

    def before_save(self):
        """Update calculations and validations before saving."""
        self._update_interaction_metadata()
        self._validate_relationship_consistency()

    def on_submit(self):
        """Process interaction completion with proper validation."""
        self._validate_interaction_completion()
        self._update_related_instruments()
        self._synchronize_repair_status()

    def _validate_required_fields(self):
        """Validate all required fields are present."""
        required_fields = ["interaction_type"]
        missing = [field for field in required_fields if not self.get(field)]
        if missing:
            frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))

    def _validate_instrument_references(self):
        """Validate instrument references exist and are accessible."""
        # Validate primary instrument if specified
        if self.primary_instrument:
            if not frappe.db.exists('Instrument Profile', self.primary_instrument):
                frappe.throw(_("Primary instrument {0} does not exist").format(self.primary_instrument))
            
            if not frappe.has_permission("Instrument Profile", "read", self.primary_instrument):
                frappe.throw(_("No permission to access instrument {0}").format(self.primary_instrument))
        
        # Validate related instrument if specified
        if self.related_instrument:
            if not frappe.db.exists('Instrument Profile', self.related_instrument):
                frappe.throw(_("Related instrument {0} does not exist").format(self.related_instrument))
            
            if not frappe.has_permission("Instrument Profile", "read", self.related_instrument):
                frappe.throw(_("No permission to access instrument {0}").format(self.related_instrument))
        
        # Prevent self-reference if both are specified
        if self.primary_instrument and self.related_instrument and self.primary_instrument == self.related_instrument:
            frappe.throw(_("Primary and related instruments cannot be the same"))

    def _validate_relationship_type(self):
        """Validate relationship type is valid for the instruments."""
        valid_relationships = [
            'Set Components',  # Clarinet body parts
            'Accessory Pairing',  # Mouthpiece, ligature, etc.
            'Backup Instrument',  # Primary/backup relationship
            'Comparison Reference',  # Used for comparison during repair
            'Replacement Part Source',  # Source of replacement parts
            'Calibration Reference',  # Reference instrument for calibration
            'Quality Control',  # QC comparison instrument
            'Other'
        ]
        
        if self.relationship_type and self.relationship_type not in valid_relationships:
            frappe.throw(_("Invalid relationship type: {0}. Valid options are: {1}").format(
                self.relationship_type, ', '.join(valid_relationships)))

    def _validate_interaction_logic(self):
        """Validate interaction logic and data consistency."""
        # Validate interaction type
        valid_interactions = [
            'Assembly', 'Disassembly', 'Comparison', 'Part Exchange',
            'Synchronized Repair', 'Quality Check', 'Calibration', 'Testing'
        ]
        
        if self.interaction_type and self.interaction_type not in valid_interactions:
            frappe.throw(_("Invalid interaction type: {0}").format(self.interaction_type))
        
        # Validate JSON fields
        if self.interaction_details:
            try:
                json.loads(self.interaction_details)
            except json.JSONDecodeError:
                frappe.throw(_("Interaction details must be valid JSON format"))
        
        # Validate impact level
        if self.impact_level and self.impact_level not in ['None', 'Low', 'Medium', 'High', 'Critical']:
            frappe.throw(_("Invalid impact level: {0}").format(self.impact_level))

    def _validate_user_permissions(self):
        """Validate user has appropriate permissions for the interaction."""
        if self.performed_by:
            # Verify user exists and is active
            user_data = frappe.db.get_value('User', self.performed_by, ['enabled', 'full_name'])
            
            if not user_data or not user_data[0]:
                frappe.throw(_('User {0} is not active in the system.').format(self.performed_by))
            
            # Check for appropriate roles
            required_roles = ['Technician', 'Repair Specialist', 'System Manager']
            user_roles = frappe.get_roles(self.performed_by)
            
            if not any(role in user_roles for role in required_roles):
                frappe.msgprint(_('Warning: User {0} may not have appropriate permissions for instrument interactions.').format(self.performed_by))

    def _set_interaction_timestamp(self):
        """Set interaction timestamp if not specified."""
        if not self.interaction_timestamp:
            self.interaction_timestamp = now_datetime()

    def _normalize_relationship_data(self):
        """Normalize and structure relationship data."""
        # Create structured relationship summary
        relationship_summary = {
            'primary_instrument': self.primary_instrument,
            'related_instrument': self.related_instrument,
            'relationship_type': self.relationship_type,
            'interaction_type': self.interaction_type,
            'timestamp': str(self.interaction_timestamp),
            'performed_by': self.performed_by
        }
        
        # Store relationship metadata
        if not self.relationship_metadata:
            self.relationship_metadata = json.dumps(relationship_summary, indent=2, default=str)

    def _validate_cross_references(self):
        """Validate cross-references between related documents."""
        # Check for existing relationships if both instruments specified
        if self.primary_instrument and self.related_instrument and self.relationship_type:
            existing_relationship = frappe.db.exists(self.doctype, {
                'name': ['!=', self.name],
                'primary_instrument': self.primary_instrument,
                'related_instrument': self.related_instrument,
                'relationship_type': self.relationship_type,
                'docstatus': ['!=', 2]
            })
            
            if existing_relationship:
                frappe.msgprint(_("Warning: Similar relationship already exists: {0}").format(existing_relationship))

    def _update_interaction_metadata(self):
        """Update interaction metadata with current values."""
        try:
            metadata = json.loads(self.relationship_metadata or '{}')
            metadata.update({
                'last_modified': str(now_datetime()),
                'modified_by': frappe.session.user,
                'interaction_count': metadata.get('interaction_count', 0) + 1
            })
            self.relationship_metadata = json.dumps(metadata, indent=2, default=str)
        except json.JSONDecodeError:
            # Reset metadata if corrupted
            self._normalize_relationship_data()

    def _validate_relationship_consistency(self):
        """Validate relationship data consistency."""
        # Only validate if both instruments are specified
        if not (self.primary_instrument and self.related_instrument and self.relationship_type):
            return
            
        # Check for conflicting relationships
        if self.relationship_type == 'Set Components':
            # Ensure instruments are compatible for set components
            primary_model = frappe.db.get_value('Instrument Profile', self.primary_instrument, 'instrument_model')
            related_model = frappe.db.get_value('Instrument Profile', self.related_instrument, 'instrument_model')
            
            if primary_model and related_model and primary_model != related_model:
                frappe.msgprint(_("Warning: Set components from different instrument models"))

    def _validate_interaction_completion(self):
        """Validate interaction is complete before submission."""
        if not self.performed_by:
            frappe.throw(_("Performed by field is required for submission"))
        
        if not self.interaction_timestamp:
            frappe.throw(_("Interaction timestamp is required for submission"))
        
        if self.impact_level in ['High', 'Critical'] and not self.notes:
            frappe.throw(_("Notes are required for high-impact interactions"))

    def _update_related_instruments(self):
        """Update related instruments with interaction information."""
        if not (self.primary_instrument and self.related_instrument):
            return
            
        try:
            # Update primary instrument
            primary_instrument = frappe.get_doc('Instrument Profile', self.primary_instrument)
            
            # Add to related instruments list if field exists
            if hasattr(primary_instrument, 'related_instruments'):
                related_list = json.loads(primary_instrument.related_instruments or '[]')
                
                relationship_record = {
                    'instrument_id': self.related_instrument,
                    'relationship_type': self.relationship_type,
                    'last_interaction': str(self.interaction_timestamp),
                    'interaction_type': self.interaction_type
                }
                
                # Remove existing entry and add updated one
                related_list = [r for r in related_list if r.get('instrument_id') != self.related_instrument]
                related_list.append(relationship_record)
                
                primary_instrument.db_set('related_instruments', json.dumps(related_list))
            
            frappe.logger("instrument_relationships").info({
                "action": "related_instruments_updated",
                "primary_instrument": self.primary_instrument,
                "related_instrument": self.related_instrument,
                "relationship_type": self.relationship_type
            })
            
        except Exception as e:
            frappe.log_error(f"Failed to update related instruments: {str(e)}")

    def _synchronize_repair_status(self):
        """Synchronize repair status between related instruments if applicable."""
        if not (self.primary_instrument and self.related_instrument and self.relationship_type):
            return
            
        if self.relationship_type in ['Set Components', 'Synchronized Repair']:
            try:
                # Get repair status of primary instrument
                primary_status = frappe.db.get_value('Instrument Profile', self.primary_instrument, 'repair_status')
                
                if primary_status and self.sync_repair_status:
                    # Update related instrument status
                    related_instrument = frappe.get_doc('Instrument Profile', self.related_instrument)
                    
                    if hasattr(related_instrument, 'repair_status'):
                        related_instrument.db_set('repair_status', primary_status)
                        
                        frappe.logger("repair_synchronization").info({
                            "action": "repair_status_synchronized",
                            "primary_instrument": self.primary_instrument,
                            "related_instrument": self.related_instrument,
                            "status": primary_status
                        })
                
            except Exception as e:
                frappe.log_error(f"Failed to synchronize repair status: {str(e)}")

    def _log_interaction_audit(self):
        """Log related instrument interaction for audit compliance."""
        frappe.logger("instrument_interaction_audit").info({
            "action": "related_instrument_interaction",
            "primary_instrument": self.primary_instrument,
            "related_instrument": self.related_instrument,
            "relationship_type": self.relationship_type,
            "interaction_type": self.interaction_type,
            "performed_by": self.performed_by,
            "impact_level": self.impact_level,
            "user": frappe.session.user,
            "timestamp": str(self.interaction_timestamp)
        })

    @frappe.whitelist()
    def get_relationship_history(self):
        """Get interaction history between these instruments."""
        if not frappe.has_permission(self.doctype, "read"):
            frappe.throw(_("No permission to view relationship history"))
        
        if not (self.primary_instrument and self.related_instrument):
            return []
        
        # Get bidirectional relationship history
        history = frappe.get_all(self.doctype,
            filters=[
                ['docstatus', '!=', 2],
                [
                    ['primary_instrument', '=', self.primary_instrument],
                    ['related_instrument', '=', self.related_instrument]
                ],
                'or',
                [
                    ['primary_instrument', '=', self.related_instrument],
                    ['related_instrument', '=', self.primary_instrument]
                ]
            ],
            fields=[
                'name', 'interaction_timestamp', 'relationship_type', 
                'interaction_type', 'performed_by', 'impact_level'
            ],
            order_by='interaction_timestamp desc',
            limit=50
        )
        
        return history
