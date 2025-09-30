// Path: repair_portal/repair_portal/customer/doctype/linked_players/linked_players.js
// Date: 2025-01-27
// Version: 3.0.0
// Description: Client-side controller for Linked Players with validation, auto-completion, and relationship management
// Dependencies: frappe, Player Profile, Person

frappe.ui.form.on("Linked Players", {
    /**
     * Form rendering with defaults and validation setup
     */
    form_render: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        
        // Set default relationship if blank
        if (!row.relationship) {
            frappe.model.set_value(cdt, cdn, "relationship", "Self");
        }
        
        // Set default date_linked to today if blank
        if (!row.date_linked) {
            frappe.model.set_value(cdt, cdn, "date_linked", frappe.datetime.get_today());
        }
    },
    
    /**
     * Handle player profile selection
     */
    player_profile: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        
        if (row.player_profile) {
            // Check for duplicates
            LinkedPlayersController.checkDuplicatePlayer(frm, cdt, cdn);
            
            // Load player details
            LinkedPlayersController.loadPlayerDetails(frm, cdt, cdn);
            
            // Auto-suggest person if linked to player profile
            LinkedPlayersController.suggestLinkedPerson(frm, cdt, cdn);
        }
    },
    
    /**
     * Handle person selection
     */
    person: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        
        if (row.person) {
            LinkedPlayersController.loadPersonDetails(frm, cdt, cdn);
        }
    },
    
    /**
     * Handle primary flag changes
     */
    is_primary: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        
        if (row.is_primary) {
            LinkedPlayersController.enforceSinglePrimary(frm, cdt, cdn);
        }
    },
    
    /**
     * Validate relationship type
     */
    relationship: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        LinkedPlayersController.validateRelationship(frm, cdt, cdn);
    }
});

/**
 * Controller class for Linked Players functionality
 */
class LinkedPlayersController {
    
    /**
     * Check for duplicate player profiles in the same customer
     */
    static checkDuplicatePlayer(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const playerProfile = row.player_profile;
        
        if (!playerProfile) return;
        
        // Check siblings for duplicates
        const fieldname = row.parentfield;
        const siblings = frm.doc[fieldname] || [];
        
        const duplicates = siblings.filter(d => 
            d.player_profile === playerProfile && d.name !== row.name
        );
        
        if (duplicates.length > 0) {
            frappe.msgprint({
                title: __('Duplicate Player'),
                message: __('This Player Profile is already linked to this customer'),
                indicator: 'red'
            });
            frappe.model.set_value(cdt, cdn, 'player_profile', '');
            return;
        }
    }
    
    /**
     * Load player profile details
     */
    static loadPlayerDetails(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        
        if (!row.player_profile) return;
        
        frappe.db.get_doc('Player Profile', row.player_profile).then(player => {
            frappe.model.set_value(cdt, cdn, 'player_name', player.player_name);
            frappe.model.set_value(cdt, cdn, 'instrument_category', player.instrument_category);
            frappe.model.set_value(cdt, cdn, 'skill_level', player.skill_level);
            
            // Show player info
            if (player.player_name) {
                frappe.show_alert({
                    message: __('Loaded: {0} ({1})', [player.player_name, player.instrument_category]),
                    indicator: 'green'
                });
            }
        });
    }
    
    /**
     * Suggest linked person from player profile
     */
    static suggestLinkedPerson(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        
        if (!row.player_profile || row.person) return;
        
        frappe.db.get_value('Player Profile', row.player_profile, 'linked_person').then(r => {
            if (r.message && r.message.linked_person) {
                frappe.model.set_value(cdt, cdn, 'person', r.message.linked_person);
                frappe.show_alert({
                    message: __('Auto-linked person from player profile'),
                    indicator: 'blue'
                });
            }
        });
    }
    
    /**
     * Load person details
     */
    static loadPersonDetails(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        
        if (!row.person) return;
        
        frappe.db.get_doc('Person', row.person).then(person => {
            const fullName = [person.first_name, person.last_name].filter(n => n).join(' ');
            frappe.model.set_value(cdt, cdn, 'person_name', fullName);
            frappe.model.set_value(cdt, cdn, 'contact_email', person.email);
            frappe.model.set_value(cdt, cdn, 'contact_mobile', person.mobile_no);
        });
    }
    
    /**
     * Enforce single primary player per customer
     */
    static enforceSinglePrimary(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const fieldname = row.parentfield;
        const siblings = frm.doc[fieldname] || [];
        
        // Clear other primary flags
        siblings.forEach(d => {
            if (d.name !== row.name && d.is_primary) {
                frappe.model.set_value(d.doctype, d.name, 'is_primary', 0);
            }
        });
        
        frappe.show_alert({
            message: __('Set as primary player'),
            indicator: 'green'
        });
    }
    
    /**
     * Validate relationship type
     */
    static validateRelationship(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const allowedRelationships = [
            'Self', 'Parent', 'Guardian', 'Teacher', 'Student',
            'Family Member', 'Friend', 'Other'
        ];
        
        if (row.relationship && !allowedRelationships.includes(row.relationship)) {
            frappe.msgprint({
                title: __('Invalid Relationship'),
                message: __('Please select a valid relationship type'),
                indicator: 'red'
            });
            frappe.model.set_value(cdt, cdn, 'relationship', 'Other');
        }
    }
    
    /**
     * Show player details dialog
     */
    static showPlayerDetails(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        
        if (!row.player_profile) {
            frappe.msgprint(__('Please select a player profile first'));
            return;
        }
        
        frappe.call({
            method: 'repair_portal.customer.doctype.linked_players.linked_players.get_player_details',
            args: {
                player_profile: row.player_profile
            },
            callback: function(r) {
                if (r.message) {
                    const data = r.message;
                    const html = `
                        <div class="row">
                            <div class="col-md-6">
                                <h5>Player Information</h5>
                                <p><strong>Name:</strong> ${data.player_name || 'N/A'}</p>
                                <p><strong>Instrument:</strong> ${data.instrument_category || 'N/A'}</p>
                                <p><strong>Skill Level:</strong> ${data.skill_level || 'N/A'}</p>
                                <p><strong>Date of Birth:</strong> ${data.date_of_birth || 'N/A'}</p>
                            </div>
                            <div class="col-md-6">
                                <h5>Status</h5>
                                <p><strong>Workflow State:</strong> ${data.workflow_state || 'N/A'}</p>
                                <p><strong>Instruments Owned:</strong> ${data.instruments_owned || 0}</p>
                                <p><strong>Performance History:</strong> ${data.performance_history || 0}</p>
                                <p><strong>Last Updated:</strong> ${frappe.datetime.str_to_user(data.last_updated) || 'N/A'}</p>
                            </div>
                        </div>
                    `;
                    
                    frappe.msgprint({
                        title: __('Player Details'),
                        message: html,
                        wide: true
                    });
                }
            }
        });
    }
}

// Add custom buttons to Customer form for player management
frappe.ui.form.on("Customer", {
    refresh: function(frm) {
        if (frm.doc.linked_players && frm.doc.linked_players.length > 0) {
            frm.add_custom_button(__('View Player Details'), function() {
                const players = frm.doc.linked_players;
                if (players.length === 1) {
                    LinkedPlayersController.showPlayerDetails(frm, players[0].doctype, players[0].name);
                } else {
                    // Show selection dialog for multiple players
                    const options = players.map(p => ({
                        label: p.player_name || p.player_profile,
                        value: p
                    }));
                    
                    frappe.prompt({
                        label: 'Select Player',
                        fieldname: 'player',
                        fieldtype: 'Select',
                        options: options.map(o => o.label),
                        reqd: 1
                    }, function(values) {
                        const selected = options.find(o => o.label === values.player);
                        if (selected) {
                            LinkedPlayersController.showPlayerDetails(frm, selected.value.doctype, selected.value.name);
                        }
                    }, __('Select Player to View'));
                }
            }, __('Players'));
        }
    }
});