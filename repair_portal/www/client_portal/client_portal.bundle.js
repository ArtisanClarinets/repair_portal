import { createApp } from "vue";
import App from "./clarinet_profile.vue";

class ClarinetProfile {
  constructor({ wrapper, page }) {
    this.$wrapper = $(wrapper);
    this.page = page;
    this.init();
  }

  init() {
    this.setup_app();
  }

  setup_app() {
    let app = createApp(App);
    this.$clarinet_profile = app.mount(this.$wrapper.get(0));
  }
}

frappe.provide("frappe.ui");
frappe.ui.ClarinetProfile = ClarinetProfile;
export default ClarinetProfile;
