frappe.ui.form.on('Clarinet Intake', {
    refresh(frm) {
        // System Manager or Repair Manager: quick link to Settings
        if (
            frappe.user.has_role('System Manager') ||
            frappe.user.has_role('Repair Manager')
        ) {
            frm.add_custom_button(
                __('Settings'),
                () => frappe.set_route('Form', 'Clarinet Intake Settings'),
                __('Actions')
            );
        }
        // Only show Inspection/Setup links after save
        if (frm.doc.__islocal) return;
        // 1. Use whitelisted method for Instrument Inspection link
        frappe.call({
            method: 'repair_portal.intake.doctype.clarinet_intake.clarinet_intake.get_instrument_inspection_name',
            args: { intake_record_id: frm.doc.name },
            callback: function(r) {
                if (r.message) {
                    frm.add_custom_button(
                        __('Instrument Inspection'),
                        () => frappe.set_route('Form', 'Instrument Inspection', r.message),
                        __('View')
                    );
                }
            }
        });
        // 2. For New Inventory: link to Initial Setup if exists
        if (frm.doc.intake_type === 'New Inventory' && frm.doc.instrument) {
            frappe.db.get_list('Clarinet Initial Setup', {
                filters: { instrument: frm.doc.instrument },
                fields: ['name']
            }).then(res => {
                if (res && res.length > 0) {
                    frm.add_custom_button(
                        __('Initial Setup'),
                        () => frappe.set_route('Form', 'Clarinet Initial Setup', res[0].name),
                        __('View')
                    );
                }
            });
        }
    },
    intake_type(frm) {
        // Refresh required fields depending on intake type
        const required_fields = {
            'New Inventory': ['item_code', 'item_name', 'acquisition_cost', 'store_asking_price'],
            'Repair': ['customer', 'customers_stated_issue'],
            'Maintenance': ['customer', 'customers_stated_issue'],
        };
        Object.keys(required_fields).forEach(type => {
            (required_fields[type] || []).forEach(field => {
                frm.toggle_reqd(field, frm.doc.intake_type === type);
            });
        });
    },
    serial_no(frm) {
        // Autofill from Instrument by Serial No
        if (frm.doc.serial_no) {
            frappe.call({
                method: 'repair_portal.intake.doctype.clarinet_intake.clarinet_intake.get_instrument_by_serial',
                args: { serial_no: frm.doc.serial_no },
                callback: r => {
                    if (r.message) {
                        Object.keys(r.message).forEach(key => {
                            if (!frm.doc[key]) {
                                frm.set_value(key, r.message[key]);
                            }
                        });
                    }
                }
            });
        }
    }
});
