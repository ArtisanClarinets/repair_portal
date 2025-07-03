frappe.pages["profile-view"].on_page_load = function (wrapper) {
    frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Profile View"),
        single_column: true,
    });
};

frappe.pages["profile-view"].on_page_show = function (wrapper) {
    load_page(wrapper);
};

function load_page(wrapper) {
    let $parent = $(wrapper).find(".layout-main-section");
    $parent.empty();

    frappe.require("profile_view.bundle.js").then(() => {
        frappe.profile_view = new frappe.ui.ProfileView({
            wrapper: $parent,
            page: wrapper.page,
        });
    });
}
