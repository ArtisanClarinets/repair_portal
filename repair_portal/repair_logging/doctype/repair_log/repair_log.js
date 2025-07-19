// File: repair_portal/repair_logging/doctype/repair_log/repair_log.js
// Last Updated: 2025-07-19
// Version: v1.0
// Purpose: Client-side controller for Repair Log; enables UI polish and field logic.

frappe.ui.form.on('Repair Log', {
    refresh(frm) {
        if (frm.doc.status) {
            let color = frm.doc.status === "Open" ? "orange"
                : frm.doc.status === "In Progress" ? "blue"
                : frm.doc.status === "Complete" ? "green"
                : frm.doc.status === "Cancelled" ? "red" : "gray";
            frm.dashboard.clear_indicators && frm.dashboard.clear_indicators();
            frm.dashboard.add_indicator(frm.doc.status, color);
        }
    },
    instrument(frm) {
        if (frm.doc.instrument && !frm.doc.customer) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Instrument',
                    name: frm.doc.instrument
                },
                callback: function(r) {
                    if (r.message && r.message.customer) {
                        frm.set_value('customer', r.message.customer);
                    }
                }
            });
        }
    },
    validate(frm) {
        let missing = [];
        if (!frm.doc.instrument) missing.push("Instrument");
        if (!frm.doc.technician) missing.push("Technician");
        if (!frm.doc.summary) missing.push("Summary");
        if (!frm.doc.date) missing.push("Date");
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
