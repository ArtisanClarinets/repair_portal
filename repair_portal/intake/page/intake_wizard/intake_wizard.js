frappe.pages["intake_wizard"].on_page_load = function (wrapper) {
    frappe.ui.make_app_page({
        parent: wrapper,
        title: __("intake_wizard"),
        single_column: true,
    });
};

frappe.pages["intake_wizard"].on_page_show = function (wrapper) {
    load_desk_page(wrapper);
};

function load_desk_page(wrapper) {
    let $parent = $(wrapper).find(".layout-main-section");
    $parent.empty();

    frappe.require("intake_wizard.bundle.js").then(() => {
        frappe.intake_wizard = new frappe.ui.Intake_Wizard({
            wrapper: $parent,
            page: wrapper.page,
        });
    });
}
