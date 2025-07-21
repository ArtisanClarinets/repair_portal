// Version: v3.7 – 2025-07-21
// Changelog:
//   • PATCH: migrate instrument_unique_id → instrument everywhere.
//   • PATCH: clarify all field sets for orchestration and controller alignment.

frappe.ui.form.on('Clarinet Intake', {
    onload(frm) {
        // Set default status
        if (!frm.doc.intake_status) {
            frm.set_value('intake_status', 'Pending');
        }
        // NEW → show/hide/require the right fields immediately
        frm.trigger('toggle_fields_by_type');
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
                frm.set_value('instrument', inst.name); // PATCH: renamed field
                [
                    'manufacturer',
                    'model',
                    'clarinet_type',
                    'year_of_manufacture',
                    'body_material',
                    'key_plating',
                    'pitch_standard',
                ].forEach(f => {
                    if (!frm.doc[f] && inst[f]) frm.set_value(f, inst[f]);
                });
            },
        });
    },

    toggle_fields_by_type(frm) {
        const t = frm.doc.intake_type || 'New Inventory';
        const inv = t === 'New Inventory';
        const reqd = (fields, flag) => fields.forEach(f => frm.toggle_reqd(f, flag));

        // Customer‐flow
        reqd(['customer', 'customers_stated_issue', 'service_type_requested'], !inv);
        // Inventory‐flow
        reqd(
            [
                'body_material',
                'acquisition_source',
                'acquisition_cost',
                'store_asking_price',
                'item_code',
                'item_name',
            ],
            inv
        );
        // PATCH: Clear customer when switching to Inventory
        if (inv) frm.set_value('customer', "");
    },

    validate(frm) {
        const map = {
            'New Inventory': [
                'body_material',
                'acquisition_source',
                'acquisition_cost',
                'store_asking_price',
                'item_code',
                'item_name',
            ],
            Repair: ['customers_stated_issue', 'service_type_requested', 'customer'],
            Maintenance: ['customers_stated_issue', 'service_type_requested', 'customer'],
        };
        (map[frm.doc.intake_type] || []).forEach(f => {
            if (!frm.doc[f]) {
                frappe.msgprint({
                    title: __('Validation Error'),
                    message: __(
                        'Field {0} is required for {1} intake type.',
                        [__(f), __(frm.doc.intake_type)]
                    ),
                    indicator: 'red',
                });
                frappe.validated = false;
            }
        });
    },

    refresh(frm) {
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
    },
});

frappe.listview_settings['Clarinet Intake'] = {
    onload(listview) {
        if (
            frappe.user.has_role('System Manager') ||
            frappe.user.has_role('Repair Manager')
        ) {
            listview.page.add_menu_item(__('Settings'), () =>
                frappe.set_route('Form', 'Clarinet Intake Settings')
            );
        }
    },
};
// File: intake/doctype/clarinet_intake/clarinet_intake.js
// Last Updated: 2025-07-21
// Version: v3.7
// Purpose: Dynamic form handling for Clarinet Intake