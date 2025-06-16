// JS Controller for Intake Master Console
frappe.pages['intake_master_console'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Intake Master Console',
        single_column: true
    });

    frappe.call({
        method: 'repair_portal.intake.page.intake_master_console.utils.get_console_data',
        callback: function(r) {
            if (r.message) {
                $(wrapper).find('#intake-dashboard').html(r.message);
            }
        }
    });
};