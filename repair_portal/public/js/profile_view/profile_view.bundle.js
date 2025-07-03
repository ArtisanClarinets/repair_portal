import { createApp } from 'vue';
import ProfileView from './ProfileView.vue';

class ProfileViewPage {
  constructor({ wrapper, page }) {
    this.$wrapper = $(wrapper);
    this.page = page;
    this.init();
  }

  init() {
    this.setup_page_actions();
    this.mount_app();
  }

  setup_page_actions() {
    // Add actions if needed in the future
  }

  mount_app() {
    this.$wrapper.html('<div id="__profile_view_app__"></div>');
    const container = this.$wrapper.find('#__profile_view_app__').get(0);
    const app = createApp(ProfileView);
    app.mount(container);
    this.vueApp = app;
  }
}

frappe.provide('frappe.ui');
frappe.ui.ProfileView = ProfileViewPage;
export default ProfileViewPage;
