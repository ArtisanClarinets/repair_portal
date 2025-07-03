frappe.pages["intake-dashboard"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Intake Dashboard"),
		single_column: true,
	});
};

frappe.pages["intake-dashboard"].on_page_show = function (wrapper) {
	load_desk_page(wrapper);
};

function load_desk_page(wrapper) {
	let $parent = $(wrapper).find(".layout-main-section");
	$parent.empty();

	frappe.require("intake_dashboard.bundle.js").then(() => {
		frappe.intake_dashboard = new frappe.ui.IntakeDashboard({
			wrapper: $parent,
			page: wrapper.page,
		});
	});
}