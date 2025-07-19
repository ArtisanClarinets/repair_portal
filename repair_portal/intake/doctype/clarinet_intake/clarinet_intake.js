// File: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.js
// Last Updated: 2025-07-19
// Version: v2.1
// Purpose: Unified UI logic for Clarinet Intake—Inventory, Repair, Maintenance. Fortune-500 grade UX.

frappe.ui.form.on('Clarinet Intake', {
    onload(frm) {
        // Default intake_status to 'Pending' if blank
        if (!frm.doc.intake_status) {
            frm.set_value('intake_status', 'Pending');
        }
    },
    refresh(frm) {
        // Status indicator
        if (frm.doc.intake_status) {
            let color = frm.doc.intake_status === "Pending" ? "orange"
                        : frm.doc.intake_status === "In Progress" ? "blue"
                        : frm.doc.intake_status === "Complete" ? "green" : "gray";
            frm.dashboard.clear_indicators && frm.dashboard.clear_indicators();
            frm.dashboard.add_indicator(frm.doc.intake_status, color);
        }
        frm.trigger('toggle_fields_by_type');
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
        // For Inventory: Show instrument selection field, hide customer fields
        frm.set_df_property('instrument', 'hidden', !is_inventory);
        frm.set_df_property('instrument', 'reqd', is_inventory);
        // Hide customer-specific fields for Inventory
        frm.set_df_property('customer', 'hidden', is_inventory);
        frm.set_df_property('customer', 'reqd', !is_inventory);
        frm.set_df_property('date_purchased', 'hidden', is_inventory);
        frm.set_df_property('customer_concerns', 'hidden', is_inventory);
        frm.refresh_fields();
    },
    validate(frm) {
        let missing = [];
        if (!frm.doc.serial_no) missing.push("Serial Number");
        if (missing.length) {
            frappe.msgprint({
                title: "Missing Required Information",
                message: "Please fill the following fields:<br>" + missing.join("<br>"),
                indicator: "red"
            });
            frappe.validated = false;
        }
    }
});
