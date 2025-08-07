frappe.pages["technician_dashboard"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("technician_dashboard"),
		single_column: true,
	});
};

frappe.pages["technician_dashboard"].on_page_show = function (wrapper) {
	load_desk_page(wrapper);
};

function load_desk_page(wrapper) {
	let $parent = $(wrapper).find(".layout-main-section");
	$parent.empty();

	frappe.require("technician_dashboard.bundle.js").then(() => {
		frappe.technician_dashboard = new frappe.ui.Technician_Dashboard({
			wrapper: $parent,
			page: wrapper.page,
		});
	});
}