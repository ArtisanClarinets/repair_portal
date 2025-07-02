import { createApp } from "vue";
import App from "./App.vue";

class Technician {
  constructor({ page, wrapper }) {
    this.$wrapper = $(wrapper);
    this.page = page;
    this.init();
  }

  init() {
    this.setup_page_actions();
    this.setup_app();
  }

  setup_page_actions() {
    // Primary action on the Desk page
    this.page.set_primary_action(
      __("Refresh Counts"),
      () => {
        // Re-mounting is heavy, so instead trigger a custom event
        this.$wrapper.find("#__technician_app__").trigger("reloadCounts");
      }
    );
  }

  setup_app() {
    // Mount the Vue App into the wrapper
    this.$wrapper.html('<div id="__technician_app__"></div>');
    this.vueApp = createApp(App);

    // Listen for manual reloads
    this.vueApp.config.globalProperties.$onReload = () => {
      this.vueApp._instance.refs.dashboard?.loadAll();
    };

    this.vueApp.mount(this.$wrapper.find("#__technician_app__").get(0));

    // Wire up the custom reload event
    this.$wrapper
      .find("#__technician_app__")
      .on("reloadCounts", () => this.vueApp._instance.ctx.$onReload());
  }
}

frappe.provide("frappe.ui");
frappe.ui.Technician = Technician;
export default Technician;
