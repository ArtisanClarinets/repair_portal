frappe.ui.form.on('Repair Order', {
    refresh(frm) {
        if (!frm.doc) {
            return;
        }
        frm.set_indicator_formatter('sla_risk', function (value) {
            if (value === 'High') {
                return 'red';
            }
            if (value === 'Medium') {
                return 'orange';
            }
            return 'green';
        });

        if (frm.doc.docstatus === 1) {
            if (frm.perm && frm.perm[0] && frm.perm[0].write) {
                frm.add_custom_button(__('Reserve Stock'), () => reserveStock(frm), __('Inventory'));
                frm.add_custom_button(__('Issue to Job'), () => issueToJob(frm), __('Inventory'));
            }
        }
    }
});

async function reserveStock(frm) {
    await frm.save();
    frappe.call({
        method: 'repair_portal.repair_portal.inventory.material_planner.reserve_stock',
        args: { repair_order: frm.doc.name },
        callback: () => frm.reload_doc()
    });
}

async function issueToJob(frm) {
    await frm.save();
    frappe.confirm(__('This will create a material issue for all planned materials. Continue?'), () => {
        frappe.call({
            method: 'repair_portal.repair_portal.inventory.material_planner.issue_to_job',
            args: { repair_order: frm.doc.name },
            callback: () => frm.reload_doc()
        });
    });
}
