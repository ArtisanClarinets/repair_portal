import { createApp } from "vue";
import App from "./App.vue";

class Intake_Wizard {
    constructor({ page, wrapper }) {
        this.$wrapper = $(wrapper);
        this.page = page;
        this.init();
    }

    init() {
        this.setup_app();
    }

    setup_app() {
        const app = createApp(App);
        this.$intake_wizard = app.mount(this.$wrapper.get(0));
    }
}

frappe.provide("frappe.ui");
frappe.ui.Intake_Wizard = Intake_Wizard;
export default Intake_Wizard;
