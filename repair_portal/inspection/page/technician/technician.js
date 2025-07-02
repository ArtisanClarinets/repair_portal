frappe.pages["technician"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Technician"),
		single_column: true,
	});
};

frappe.pages["technician"].on_page_show = function (wrapper) {
	load_desk_page(wrapper);
};

function load_desk_page(wrapper) {
	let $parent = $(wrapper).find(".layout-main-section");
	$parent.empty();

	frappe.require("technician.bundle.js").then(() => {
		frappe.technician = new frappe.ui.Technician({
			wrapper: $parent,
			page: wrapper.page,
		});
	});
}