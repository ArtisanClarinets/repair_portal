// File: public/js/repair_request.js
// Updated: 2025-06-16
// JS enhancements for Repair Request page

frappe.ready(() => {
  // Scroll to form smoothly on page load
  const form = document.querySelector("#repair-form");
  if (form) {
    form.scrollIntoView({ behavior: "smooth" });
  }

  // Auto-focus first input
  const firstInput = form?.querySelector("input, textarea, select");
  if (firstInput) {
    firstInput.focus();
  }
});