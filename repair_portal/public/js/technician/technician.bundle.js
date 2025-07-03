import { createApp } from "vue";
import App from "./App.vue";

// The class name has been changed back to 'Technician' to match what the Desk page expects.
class Technician {
  constructor({ wrapper, page }) {
    this.$wrapper = $(wrapper);
    this.page = page;
    this.init();
  }

  init() {
    this.setup_page_actions();
    this.setup_vue_app();
  }

  setup_page_actions() {
    this.page.set_primary_action(
      __("Refresh Dashboard"),
      () => {
        const appElement = this.$wrapper.find("#__technician_app__").get(0);
        if (appElement) {
          appElement.dispatchEvent(new CustomEvent("reloadDashboard"));
        }
      }
    );
  }

  setup_vue_app() {
    this.$wrapper.html('<div id="__technician_app__"></div>');
    const container = this.$wrapper.find("#__technician_app__").get(0);

    const app = createApp(App);
    app.mount(container);
    this.vueApp = app;
  }
}

// Ensure the class is attached to the frappe.ui namespace correctly.
frappe.provide("frappe.ui");
frappe.ui.Technician = Technician;
export default Technician;