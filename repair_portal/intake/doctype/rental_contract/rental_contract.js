frappe.ui.form.on('Rental Contract', {
    refresh(frm) {
        if (!frm.doc.__islocal) {
            if (frm.doc.status === 'Draft' && frm.has_perm('submit')) {
                frm.add_custom_button(__('Activate'), () => trigger_state(frm, 'Activate'), __('Status Actions'));
            }
            if (frm.doc.status === 'Active') {
                frm.add_custom_button(__('Mark Returned'), () => trigger_state(frm, 'Mark Returned'), __('Status Actions'));
            }
            if (frm.doc.delivery_note) {
                frm.add_custom_button(__('Delivery Note'), () => frappe.set_route('Form', 'Delivery Note', frm.doc.delivery_note), __('View'));
            }
            if (frm.doc.subscription) {
                frm.add_custom_button(__('Subscription'), () => frappe.set_route('Form', 'Subscription', frm.doc.subscription), __('View'));
            }
            if (frm.doc.damage_invoice) {
                frm.add_custom_button(__('Damage Invoice'), () => frappe.set_route('Form', 'Sales Invoice', frm.doc.damage_invoice), __('View'));
            }
        }
    }
});

function trigger_state(frm, action) {
    frappe.xcall('frappe.model.workflow.apply_workflow', {
        doc: frm.doc,
        action: action
    }).then(() => {
        frm.reload_doc();
    });
}
