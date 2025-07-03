// repair_portal/public/js/technician_dashboard/index.js (Source file for the bundle)

import { createApp } from 'vue';
import TechnicianDashboard from './App.vue';

// This is the mounting point in your Desk Page's HTML
const mountEl = document.querySelector("#technician-dashboard-app");

if (mountEl) {
    const app = createApp(TechnicianDashboard);

    // Make Frappe utilities available inside Vue components if needed
    app.config.globalProperties.$frappe = window.frappe;

    app.mount(mountEl);
}