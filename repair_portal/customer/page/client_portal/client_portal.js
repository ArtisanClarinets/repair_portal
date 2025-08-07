frappe.pages["client-portal"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Client Portal"),
		single_column: true,
	});
};

frappe.pages["client-portal"].on_page_show = function (wrapper) {
	load_desk_page(wrapper);
};

function load_desk_page(wrapper) {
	let $parent = $(wrapper).find(".layout-main-section");
	$parent.empty();

	frappe.require("client_portal.bundle.js")
		.then(() => {
			frappe.client_portal = new frappe.ui.ClientPortal({
				wrapper: $parent,
				page: wrapper.page,
			});
		})
		.catch(() => {
			$parent.append(`<div class="alert alert-danger">Unable to load portal resources. Please refresh or contact support.</div>`);
		});
}