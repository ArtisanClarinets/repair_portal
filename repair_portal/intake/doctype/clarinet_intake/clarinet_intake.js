// File: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.js
// Version: v3.3

frappe.ui.form.on('Clarinet Intake', {
    onload(frm) {
        if (!frm.doc.intake_status) frm.set_value('intake_status', 'Pending');
    },

    intake_type(frm) {
        frm.trigger('toggle_fields_by_type');
    },

    serial_no(frm) {
        if (!frm.doc.serial_no) return;
        frappe.call({
            method: 'repair_portal.intake.doctype.clarinet_intake.clarinet_intake.get_instrument_by_serial',
            args: { serial_no: frm.doc.serial_no },
            freeze: true,
            callback: r => {
                if (!r.message) return;
                const inst = r.message;
                frm.set_value('instrument_unique_id', inst.name);
                ['manufacturer', 'model', 'clarinet_type', 'year_of_manufacture',
                    'body_material', 'keywork_plating', 'pitch_standard']
                    .forEach(f => {
                        if (!frm.doc[f] && inst[f]) frm.set_value(f, inst[f]);
                    });
            }
        });
    },

    toggle_fields_by_type(frm) {
        // Set required fields based on Intake Type, including item_code/item_name for Inventory
        const t = frm.doc.intake_type || 'New Inventory';
        const inv = t === 'New Inventory';
        const reqd = (fields, flag) => fields.forEach(f => frm.toggle_reqd(f, flag));

        reqd(['customer', 'customers_stated_issue', 'service_type_requested'], !inv);
        reqd(['body_material', 'acquisition_source', 'acquisition_cost', 'store_asking_price', 'item_code', 'item_name'], inv);
        frm.toggle_reqd('consent_liability_waiver', !inv);
    },

    validate(frm) {
        // Client-side validation including item_code and item_name for New Inventory
        const map = {
            'New Inventory': ['body_material', 'acquisition_source', 'acquisition_cost', 'store_asking_price', 'item_code', 'item_name'],
            'Repair': ['customers_stated_issue', 'service_type_requested', 'customer'],
            'Maintenance': ['customers_stated_issue', 'service_type_requested', 'customer']
        };
        const missing = (map[frm.doc.intake_type] || []).filter(f => !frm.doc[f])
            .map(f => frm.get_field(f).label);
        if (missing.length) {
            frappe.msgprint({
                title: 'Missing Required Information',
                message: `Please fill:<br>${missing.join('<br>')}`,
                indicator: 'red'
            });
            frappe.validated = false;
        }
    },

    refresh(frm) {
        // Add Settings button for managers/admins
        if (frappe.user.has_role("System Manager") || frappe.user.has_role("Repair Manager")) {
            frm.add_custom_button(__('Settings'), () => {
                frappe.set_route('Form', 'Clarinet Intake Settings');
            }, __('Actions'));
        }
    }
});

frappe.listview_settings['Clarinet Intake'] = {
    onload: function(listview) {
        if (frappe.user.has_role("System Manager") || frappe.user.has_role("Repair Manager")) {
            listview.page.add_menu_item(__('Settings'), function() {
                frappe.set_route('Form', 'Clarinet Intake Settings');
            });
        }
    }
};
