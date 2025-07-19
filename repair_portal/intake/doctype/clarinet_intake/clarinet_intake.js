// File: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.js
// Last Updated: 2025-07-18
// Version: v2.0
// Purpose: Unified UI logic for Clarinet Intake—Inventory, Repair, Maintenance. Fortune-500 grade UX.

frappe.ui.form.on('Clarinet Intake', {
    onload(frm) {
        // Default intake_status to 'Pending' if blank
        if (!frm.doc.intake_status) {
            frm.set_value('intake_status', 'Pending');
        }
    },
    refresh(frm) {
        frm.trigger('toggle_fields_by_type');
        // Modern intake status indicator (v15+ API)
        if (frm.doc.intake_status) {
            let color = frm.doc.intake_status === "Pending" ? "orange"
                        : frm.doc.intake_status === "In Progress" ? "blue"
                        : frm.doc.intake_status === "Complete" ? "green" : "gray";
            frm.dashboard.clear_indicators && frm.dashboard.clear_indicators();
            frm.dashboard.add_indicator(frm.doc.intake_status, color);
        }
    },
    intake_type(frm) {
        frm.trigger('toggle_fields_by_type');
        // Clear instrument-related fields when switching types
        if (frm.doc.intake_type === 'Inventory') {
            frm.set_value('customer', '');
            frm.set_value('date_purchased', '');
            frm.set_value('customer_concerns', '');
        } else {
            frm.set_value('instrument', '');
        }
    },
    
    // Auto-fetch instrument details when instrument is selected for Inventory type
    instrument(frm) {
        if (frm.doc.intake_type === 'Inventory' && frm.doc.instrument) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Instrument',
                    name: frm.doc.instrument
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('instrument_type', r.message.instrument_type || '');
                        frm.set_value('brand', r.message.brand || '');
                        frm.set_value('model', r.message.model || '');
                        frm.set_value('serial_no', r.message.serial_no || '');
                    }
                }
            });
        }
    },
    
    toggle_fields_by_type(frm) {
        const is_inventory = frm.doc.intake_type === 'Inventory';
        const is_repair_or_maint = frm.doc.intake_type === 'Repair' || frm.doc.intake_type === 'Maintenance';
        
        // For Inventory: Show instrument selection field, hide customer fields
        frm.set_df_property('instrument', 'hidden', !is_inventory);
        frm.set_df_property('instrument', 'reqd', is_inventory);
        
        // Hide customer-specific fields for Inventory
        frm.set_df_property('customer', 'hidden', is_inventory);
        frm.set_df_property('customer', 'reqd', !is_inventory);
        frm.set_df_property('date_purchased', 'hidden', is_inventory);
        frm.set_df_property('customer_concerns', 'hidden', is_inventory);
        
        // Show/hide other fields based on type
        const inventory_only_fields = ['item_code', 'environment_log', 'clarinet_initial_setup', 'diagnostic_metrics', 'tenon_fit_log'];
        const repair_maint_fields = ['visual_inspection', 'technician_remarks', 'notes', 'attachments'];
        
        inventory_only_fields.forEach(f => {
            if (frm.fields_dict[f]) {
                frm.set_df_property(f, 'hidden', !is_inventory);
            }
        });
        
        repair_maint_fields.forEach(f => {
            if (frm.fields_dict[f]) {
                frm.set_df_property(f, 'hidden', is_inventory);
            }
        });
        
        // Requirements for Inventory
        if (is_inventory) {
            frm.set_df_property('brand', 'reqd', false); // Will be auto-filled
            frm.set_df_property('model', 'reqd', false); // Will be auto-filled
            frm.set_df_property('instrument_type', 'reqd', false); // Will be auto-filled
            frm.set_df_property('serial_no', 'reqd', false); // Will be auto-filled
        }
        
        frm.refresh_fields();
    },
    validate(frm) {
        let missing = [];
        // Serial always required
        if (!frm.doc.serial_no) missing.push("Serial Number");
        // Inventory-specific required fields
        if (frm.doc.intake_type === 'Inventory') {
            ['item_code', 'brand', 'model', 'instrument_type'].forEach(field => {
                if (!frm.doc[field]) missing.push(frm.fields_dict[field]?.df?.label || field);
            });
        }
        // For Repair or Maintenance: customer_consent_form required?
        // (Assume this is still a field, based on prior scripts)
        if ((frm.doc.intake_type === 'Repair' || frm.doc.intake_type === 'Maintenance') && !frm.doc.customer_consent_form) {
            missing.push("Consent/Liability Waiver (for Repair/Maintenance)");
        }
        if (missing.length) {
            frappe.msgprint({
                title: "Missing Required Information",
                message: "Please fill the following fields:<br>" + missing.join("<br>"),
                indicator: "red"
            });
            frappe.validated = false;
        }
        // Optional: Email/Phone validation (can add here if you want it for both repair/maintenance)
        let email = frm.doc.email;
        if (email && !/.+@.+\..+/.test(email)) {
            frappe.show_alert({message: "Please enter a valid email address.", indicator: 'orange'});
        }
        let phone = frm.doc.phone;
        if (phone && phone.replace(/\D/g, '').length < 10) {
            frappe.show_alert({message: "Please enter a valid phone number.", indicator: 'orange'});
        }
    },
    customer_consent_form(frm) {
        if ((frm.doc.intake_type === "Repair" || frm.doc.intake_type === "Maintenance") && !frm.doc.customer_consent_form) {
            frappe.show_alert({message: "Consent/Liability Waiver is required for Repair or Maintenance.", indicator: 'red'});
        }
    }
});
