frappe.pages['bore_profile_scanner'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Bore Profile Scanner',
        single_column: true
    });

    page.add_inner_button('Upload CSV', () => {
        const dialog = new frappe.ui.Dialog({
            title: 'Upload Bore Data',
            fields: [
                {
                    label: 'CSV File',
                    fieldname: 'csv_file',
                    fieldtype: 'Attach',
                    reqd: 1
                }
            ],
            primary_action_label: 'Submit',
            primary_action(values) {
                frappe.msgprint('Data uploaded! Visualization coming soon.');
                dialog.hide();
            }
        });
        dialog.show();
    });
};