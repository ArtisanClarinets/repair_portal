import { createApp } from "vue";
import App from "./App.vue";

class ClientPortal {
	constructor({ wrapper, page }) {
		this.$wrapper = $(wrapper);
		this.page = page;
		this.init();
	}

	init() {
	    this.setup_app();
	}

	setup_app() {
		// create a vue instance
		let app = createApp(App);
		// mount the app
		this.$client_portal = app.mount(this.$wrapper.get(0));
	}
}

frappe.provide("frappe.ui");
frappe.ui.ClientPortal = ClientPortal;
export default ClientPortal;