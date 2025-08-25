// /home/frappe/frappe-bench/apps/repair_portal/repair_portal/repair/doctype/repair_quotation/repair_quotation.js
frappe.ui.form.on('Repair Quotation', {
    setup(frm) {
        frm.set_indicator_formatter('status', () => 'blue');
    },
    refresh(frm) {
        const can_edit = frm.perm && frm.perm[0] && frm.perm[0].write;

        // Primary action: Accept + Create Repair Order (idempotent)
        if (can_edit && frm.doc.docstatus !== 2 && frm.doc.status !== 'Accepted') {
            frm.add_custom_button('Accept (Create Repair Order)', () => {
                frappe.call({
                    method: 'repair_portal.repair.doctype.repair_quotation.repair_quotation.accept_and_make_repair_order',
                    doc: frm.doc,
                    args: { submit_repair_order: 1 },
                    freeze: true,
                    freeze_message: __('Creating Repair Order...'),
                    callback: (r) => {
                        if (r && r.message) {
                            const ro = r.message;
                            frappe.msgprint({
                                title: __('Repair Order Created'),
                                message: __('Repair Order <b>{0}</b> was created.', [ro.name]),
                                indicator: 'green'
                            });
                            frm.reload_doc();
                        }
                    }
                });
            }, 'Actions');
        }

        // Manual action: Make Repair Order (if already accepted or you prefer manual)
        if (can_edit && frm.doc.docstatus !== 2 && !frm.doc.repair_order) {
            frm.add_custom_button('Make Repair Order', () => {
                frappe.call({
                    method: 'repair_portal.repair.doctype.repair_quotation.repair_quotation.make_repair_order',
                    doc: frm.doc,
                    args: { submit_repair_order: 1 },
                    freeze: true,
                    freeze_message: __('Creating Repair Order...'),
                    callback: (r) => {
                        if (r && r.message) {
                            const ro = r.message;
                            frappe.msgprint({
                                title: __('Repair Order Created'),
                                message: __('Repair Order <b>{0}</b> was created.', [ro.name]),
                                indicator: 'green'
                            });
                            frm.reload_doc();
                        }
                    }
                });
            }, 'Actions');
        }
    },
    discount_type: mark_dirty,
    discount_percent: mark_dirty,
    discount_amount: mark_dirty,
    tax_rate: mark_dirty
});

function mark_dirty(frm) { frm.dirty(); }

frappe.ui.form.on('Repair Quotation Item', {
    qty: recalc_row,
    rate: recalc_row,
    hours: recalc_row,
    item_type: recalc_row
});

function recalc_row(frm, cdt, cdn) {
    const d = frappe.get_doc(cdt, cdn);
    const qty = parseFloat(d.qty || 0);
    const rate = parseFloat(d.rate || 0);
    d.amount = qty * rate;
    frm.refresh_field('items');
}
